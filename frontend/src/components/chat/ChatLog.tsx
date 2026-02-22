import { useEffect, useRef } from 'react';
import type { ChatEntry } from '../../types/messages';
import { DMMessage } from './DMMessage';
import { PlayerMessage } from './PlayerMessage';
import { DiceRollEvent } from './DiceRollEvent';
import { ToolUseEvent } from './ToolUseEvent';
import { TypingIndicator } from './TypingIndicator';

interface Props {
  entries: ChatEntry[];
  isTyping: boolean;
}

export function ChatLog({ entries, isTyping }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [entries, isTyping]);

  return (
    <div className="chat-log">
      {entries.map((entry) => {
        switch (entry.kind) {
          case 'dm':
            return <DMMessage key={entry.id} content={entry.content} isComplete={entry.isComplete} />;
          case 'player':
            return <PlayerMessage key={entry.id} content={entry.content} />;
          case 'dice':
            return <DiceRollEvent key={entry.id} notation={entry.notation} rolls={entry.rolls} total={entry.total} modifier={entry.modifier} />;
          case 'tool_indicator':
            return <ToolUseEvent key={entry.id} display_name={entry.display_name} />;
        }
      })}
      {isTyping && entries.every(e => e.kind !== 'dm' || ('isComplete' in e && e.isComplete)) && (
        <TypingIndicator />
      )}
      <div ref={bottomRef} />
    </div>
  );
}
