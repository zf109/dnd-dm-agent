import './App.css';
import { useReducer, useCallback, useEffect, useState } from 'react';
import type { ChatEntry, CharacterData, ServerMessage } from './types/messages';
import { useWebSocket } from './hooks/useWebSocket';
import type { WSStatus } from './hooks/useWebSocket';
import { parseCharacterMarkdown } from './services/characterParser';
import { AppHeader } from './components/layout/AppHeader';
import { MapPlaceholder } from './components/map/MapPlaceholder';
import { CharacterSidebar } from './components/sidebar/CharacterSidebar';
import { ChatLog } from './components/chat/ChatLog';
import { InputBar } from './components/input/InputBar';
import { ResizablePanels } from './components/layout/ResizablePanels';
import { SessionSetup } from './components/SessionSetup';

function generateId() {
  return Math.random().toString(36).slice(2, 10);
}

function getOrCreateSessionId(): string {
  let id = sessionStorage.getItem('dnd-session-id');
  if (!id) {
    id = generateId();
    sessionStorage.setItem('dnd-session-id', id);
  }
  return id;
}

interface SessionConfig {
  campaign: string;
  character: string;
}

interface AppState {
  chatEntries: ChatEntry[];
  isAgentTyping: boolean;
  currentDMEntryId: string | null;
  character: CharacterData | null;
  wsStatus: WSStatus;
}

type Action =
  | { type: 'ADD_PLAYER_MESSAGE'; content: string }
  | { type: 'APPEND_TEXT_CHUNK'; content: string }
  | { type: 'ADD_TOOL_INDICATOR'; display_name: string }
  | { type: 'ADD_DICE_RESULT'; notation: string; rolls: number[]; total: number; modifier: number }
  | { type: 'TURN_COMPLETE' }
  | { type: 'SET_CHARACTER'; data: CharacterData }
  | { type: 'SET_WS_STATUS'; status: WSStatus };

function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'ADD_PLAYER_MESSAGE': {
      const entry: ChatEntry = { id: generateId(), kind: 'player', content: action.content };
      return { ...state, chatEntries: [...state.chatEntries, entry], isAgentTyping: true };
    }
    case 'ADD_TOOL_INDICATOR': {
      const entry: ChatEntry = { id: generateId(), kind: 'tool_indicator', display_name: action.display_name };
      return { ...state, chatEntries: [...state.chatEntries, entry] };
    }
    case 'APPEND_TEXT_CHUNK': {
      if (state.currentDMEntryId) {
        // Append to existing DM message
        return {
          ...state,
          chatEntries: state.chatEntries.map((e) =>
            e.id === state.currentDMEntryId && e.kind === 'dm'
              ? { ...e, content: e.content + action.content }
              : e
          ),
        };
      } else {
        // Remove tool indicators, start new DM message
        const newId = generateId();
        const filtered = state.chatEntries.filter((e) => e.kind !== 'tool_indicator');
        const entry: ChatEntry = { id: newId, kind: 'dm', content: action.content, isComplete: false };
        return { ...state, chatEntries: [...filtered, entry], currentDMEntryId: newId };
      }
    }
    case 'ADD_DICE_RESULT': {
      const entry: ChatEntry = {
        id: generateId(),
        kind: 'dice',
        notation: action.notation,
        rolls: action.rolls,
        total: action.total,
        modifier: action.modifier,
      };
      return { ...state, chatEntries: [...state.chatEntries, entry] };
    }
    case 'TURN_COMPLETE': {
      return {
        ...state,
        isAgentTyping: false,
        currentDMEntryId: null,
        chatEntries: state.chatEntries
          .filter((e) => e.kind !== 'tool_indicator')
          .map((e) => (e.kind === 'dm' && !e.isComplete ? { ...e, isComplete: true } : e)),
      };
    }
    case 'SET_CHARACTER':
      return { ...state, character: action.data };
    case 'SET_WS_STATUS':
      return { ...state, wsStatus: action.status };
    default:
      return state;
  }
}

const SESSION_ID = getOrCreateSessionId();

export default function App() {
  const [session, setSession] = useState<SessionConfig | null>(null);

  if (!session) {
    return <SessionSetup onStart={(campaign, character) => setSession({ campaign, character })} />;
  }

  return <GameView session={session} />;
}

function GameView({ session }: { session: SessionConfig }) {
  const [state, dispatch] = useReducer(reducer, {
    chatEntries: [],
    isAgentTyping: false,
    currentDMEntryId: null,
    character: null,
    wsStatus: 'disconnected',
  });

  const fetchCharacter = useCallback(async () => {
    try {
      const res = await fetch(`/api/character/${session.campaign}/${session.character}`);
      if (!res.ok) return;
      const data = await res.json();
      const parsed = parseCharacterMarkdown(data.markdown);
      if (parsed) dispatch({ type: 'SET_CHARACTER', data: parsed });
    } catch {
      /* silently ignore */
    }
  }, [session.campaign, session.character]);

  const handleMessage = useCallback((msg: ServerMessage) => {
    switch (msg.type) {
      case 'text_chunk':
        dispatch({ type: 'APPEND_TEXT_CHUNK', content: msg.content });
        break;
      case 'tool_use':
        dispatch({ type: 'ADD_TOOL_INDICATOR', display_name: msg.display_name });
        break;
      case 'tool_result': {
        const r = msg.result as Record<string, unknown>;
        if (r?.notation && r?.individual_rolls) {
          dispatch({
            type: 'ADD_DICE_RESULT',
            notation: r.notation as string,
            rolls: r.individual_rolls as number[],
            total: (r.total as number) ?? 0,
            modifier: (r.modifier as number) ?? 0,
          });
        }
        break;
      }
      case 'turn_complete':
        dispatch({ type: 'TURN_COMPLETE' });
        // Refresh character after each turn
        fetchCharacter();
        break;
      case 'error':
        console.error('Agent error:', msg.error);
        dispatch({ type: 'TURN_COMPLETE' });
        break;
    }
  }, [fetchCharacter]);

  const { status: wsStatus, sendMessage } = useWebSocket(SESSION_ID, handleMessage);

  useEffect(() => {
    dispatch({ type: 'SET_WS_STATUS', status: wsStatus });
  }, [wsStatus]);

  // Load character on mount
  useEffect(() => { fetchCharacter(); }, [fetchCharacter]);

  const handleSend = useCallback((text: string) => {
    if (wsStatus !== 'connected' || state.isAgentTyping) return;
    dispatch({ type: 'ADD_PLAYER_MESSAGE', content: text });
    sendMessage({ type: 'user_input', content: text });
  }, [wsStatus, state.isAgentTyping, sendMessage]);

  const isDisabled = wsStatus !== 'connected' || state.isAgentTyping;

  return (
    <div className="app-root">
      <AppHeader campaign={session.campaign.replace(/_/g, ' ')} wsStatus={wsStatus} />
      <div className="app-body">
        <CharacterSidebar character={state.character} />
        <div className="main-area">
          <ResizablePanels
            top={<MapPlaceholder />}
            bottom={<ChatLog entries={state.chatEntries} isTyping={state.isAgentTyping} />}
          />
        </div>
      </div>
      <InputBar onSend={handleSend} disabled={isDisabled} />
    </div>
  );
}
