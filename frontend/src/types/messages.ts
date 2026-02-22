export type ServerMessageType = 'text_chunk' | 'tool_use' | 'tool_result' | 'turn_complete' | 'error' | 'open_character_sheet';

export interface TextChunkMessage { type: 'text_chunk'; content: string; }
export interface ToolUseMessage { type: 'tool_use'; tool_name: string; tool_input: Record<string, unknown>; display_name: string; }
export interface ToolResultMessage { type: 'tool_result'; result: Record<string, unknown>; }
export interface TurnCompleteMessage { type: 'turn_complete'; }
export interface ErrorMessage { type: 'error'; error: string; }
export interface OpenCharacterSheetMessage { type: 'open_character_sheet'; }
export type ServerMessage = TextChunkMessage | ToolUseMessage | ToolResultMessage | TurnCompleteMessage | ErrorMessage | OpenCharacterSheetMessage;

export type ChatEntry =
  | { id: string; kind: 'player'; content: string }
  | { id: string; kind: 'dm'; content: string; isComplete: boolean }
  | { id: string; kind: 'dice'; notation: string; rolls: number[]; total: number; modifier: number }
  | { id: string; kind: 'tool_indicator'; display_name: string };

export interface CharacterData {
  name: string;
  classLevel: string;
  race: string;
  hp_current: number;
  hp_max: number;
  ac: number;
  speed: number;
  conditions: string[];
  spell_slots_total: number;
  spell_slots_used: number;
}
