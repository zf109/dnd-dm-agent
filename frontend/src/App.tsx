import './App.css';
import { useReducer, useCallback, useEffect, useState, useRef, useMemo } from 'react';
import type { ChatEntry, CharacterData, ServerMessage } from './types/messages';
import { useWebSocket } from './hooks/useWebSocket';
import type { WSStatus } from './hooks/useWebSocket';
import { parseCharacterMarkdown } from './services/characterParser';
import { AppHeader } from './components/layout/AppHeader';
import { MapPlaceholder } from './components/map/MapPlaceholder';
import { ChatLog } from './components/chat/ChatLog';
import { InputBar } from './components/input/InputBar';
import { ResizablePanels } from './components/layout/ResizablePanels';
import { SessionSetup } from './components/SessionSetup';
import { SidebarPanel } from './components/sidebar/SidebarPanel';
import { CharacterSheetModal } from './components/character/CharacterSheetModal';

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

const SESSION_ID = getOrCreateSessionId();

function loadSavedSession(): SessionConfig | null {
  try {
    const raw = sessionStorage.getItem('dnd-session-config');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveSession(config: SessionConfig) {
  sessionStorage.setItem('dnd-session-config', JSON.stringify(config));
}

const CHAT_KEY = `dnd-chat-${SESSION_ID}`;

function loadChatEntries(): ChatEntry[] {
  try {
    const raw = sessionStorage.getItem(CHAT_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveChatEntries(entries: ChatEntry[]) {
  try {
    sessionStorage.setItem(CHAT_KEY, JSON.stringify(entries));
  } catch { /* quota exceeded — ignore */ }
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
  characterMarkdown: string | null;
  wsStatus: WSStatus;
}

type Action =
  | { type: 'ADD_PLAYER_MESSAGE'; content: string }
  | { type: 'ADD_SYSTEM_MESSAGE'; content: string; hidden?: boolean }
  | { type: 'APPEND_TEXT_CHUNK'; content: string }
  | { type: 'ADD_TOOL_INDICATOR'; display_name: string }
  | { type: 'ADD_DICE_RESULT'; notation: string; rolls: number[]; total: number; modifier: number }
  | { type: 'TURN_COMPLETE' }
  | { type: 'SET_CHARACTER'; data: CharacterData; markdown: string }
  | { type: 'SET_WS_STATUS'; status: WSStatus };

function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'ADD_PLAYER_MESSAGE': {
      const entry: ChatEntry = { id: generateId(), kind: 'player', content: action.content };
      return { ...state, chatEntries: [...state.chatEntries, entry], isAgentTyping: true };
    }
    case 'ADD_SYSTEM_MESSAGE': {
      const entry: ChatEntry = { id: generateId(), kind: 'system', content: action.content };
      return { ...state, chatEntries: [...state.chatEntries, entry] };
    }
    case 'ADD_TOOL_INDICATOR': {
      const entry: ChatEntry = { id: generateId(), kind: 'tool_indicator', display_name: action.display_name };
      return { ...state, chatEntries: [...state.chatEntries, entry] };
    }
    case 'APPEND_TEXT_CHUNK': {
      if (state.currentDMEntryId) {
        return {
          ...state,
          chatEntries: state.chatEntries.map((e) =>
            e.id === state.currentDMEntryId && e.kind === 'dm'
              ? { ...e, content: e.content + action.content }
              : e
          ),
        };
      } else {
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
      return { ...state, character: action.data, characterMarkdown: action.markdown };
    case 'SET_WS_STATUS':
      return { ...state, wsStatus: action.status };
    default:
      return state;
  }
}

export default function App() {
  const [session, setSession] = useState<SessionConfig | null>(loadSavedSession);

  const handleStart = useCallback((campaign: string, character: string) => {
    const config = { campaign, character };
    saveSession(config);
    setSession(config);
  }, []);

  if (!session) {
    return <SessionSetup onStart={handleStart} />;
  }

  return <GameView session={session} onLeave={() => {
    sessionStorage.removeItem('dnd-session-config');
    sessionStorage.removeItem(CHAT_KEY);
    setSession(null);
  }} />;
}

function GameView({ session, onLeave }: { session: SessionConfig; onLeave: () => void }) {
  const [state, dispatch] = useReducer(reducer, null, () => ({
    chatEntries: loadChatEntries(),
    isAgentTyping: false,
    currentDMEntryId: null,
    character: null,
    characterMarkdown: null,
    wsStatus: 'disconnected',
  }));

  const [sheetOpen, setSheetOpen] = useState(false);
  const [activeCharacter, setActiveCharacter] = useState(session.character);
  const hasInitialized = useRef(false);
  // True if we're resuming a previous session (chat history was restored from storage)
  const isRestoredSession = useRef(state.chatEntries.length > 0);

  const fetchCharacter = useCallback(async (characterName: string) => {
    try {
      const res = await fetch(`/api/character/${session.campaign}/${characterName}`);
      if (!res.ok) return;
      const data = await res.json();
      const parsed = parseCharacterMarkdown(data.markdown);
      if (parsed) dispatch({ type: 'SET_CHARACTER', data: parsed, markdown: data.markdown });
    } catch { /* silently ignore */ }
  }, [session.campaign]);

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
        fetchCharacter(activeCharacter);
        break;
      case 'open_character_sheet':
        setSheetOpen(true);
        break;
      case 'error':
        console.error('Agent error:', msg.error);
        dispatch({ type: 'TURN_COMPLETE' });
        break;
    }
  }, [fetchCharacter, activeCharacter]);

  const wsQueryString = useMemo(
    () => new URLSearchParams({ campaign: session.campaign, character: activeCharacter }).toString(),
    [session.campaign, activeCharacter],
  );
  const { status: wsStatus, sendMessage } = useWebSocket(SESSION_ID, handleMessage, wsQueryString);

  useEffect(() => {
    dispatch({ type: 'SET_WS_STATUS', status: wsStatus });
  }, [wsStatus]);

  useEffect(() => { fetchCharacter(activeCharacter); }, [fetchCharacter, activeCharacter]);

  // Persist chat entries to sessionStorage on every change
  useEffect(() => { saveChatEntries(state.chatEntries); }, [state.chatEntries]);

  useEffect(() => {
    if (wsStatus !== 'connected' || hasInitialized.current) return;
    hasInitialized.current = true;
    // On a restored session, skip the init message — the agent has campaign context
    // in its system prompt and the user can simply continue the conversation.
    if (isRestoredSession.current) return;
    const campaignLabel = session.campaign.replace(/_/g, ' ');
    const characterLabel = activeCharacter.replace(/_/g, ' ');
    dispatch({ type: 'ADD_SYSTEM_MESSAGE', content: `Campaign: ${campaignLabel}  ·  Character: ${characterLabel}` });
    sendMessage({
      type: 'user_input',
      content: `Session started. Campaign: "${campaignLabel}". Active character: "${characterLabel}". Please load the campaign using the campaign-guide skill and greet the player in character as the DM.`,
    });
  }, [wsStatus, session.campaign, activeCharacter, sendMessage]);

  const handleSelectCharacter = useCallback((name: string) => {
    setActiveCharacter(name);
  }, []);

  const handleSend = useCallback((text: string) => {
    if (wsStatus !== 'connected' || state.isAgentTyping) return;
    dispatch({ type: 'ADD_PLAYER_MESSAGE', content: text });
    sendMessage({ type: 'user_input', content: text });
  }, [wsStatus, state.isAgentTyping, sendMessage]);

  const isDisabled = wsStatus !== 'connected' || state.isAgentTyping;

  return (
    <div className="app-root">
      <AppHeader campaign={session.campaign.replace(/_/g, ' ')} wsStatus={wsStatus} onLeave={onLeave} />

      <div className="app-body">
        <SidebarPanel
          character={state.character}
          campaign={session.campaign}
          activeCharacter={activeCharacter}
          onOpenSheet={() => setSheetOpen(true)}
          onSelectCharacter={handleSelectCharacter}
        />

        <div className="main-area">
          <ResizablePanels
            top={<MapPlaceholder />}
            bottom={<ChatLog entries={state.chatEntries} isTyping={state.isAgentTyping} />}
          />
        </div>
      </div>

      <InputBar onSend={handleSend} disabled={isDisabled} />

      {sheetOpen && state.characterMarkdown && (
        <CharacterSheetModal
          markdown={state.characterMarkdown}
          characterName={activeCharacter}
          onClose={() => setSheetOpen(false)}
        />
      )}
    </div>
  );
}
