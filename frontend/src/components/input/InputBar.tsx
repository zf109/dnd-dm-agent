import { DiceButtons } from './DiceButtons';
import { MessageInput } from './MessageInput';

interface Props {
  onSend: (text: string) => void;
  disabled: boolean;
}

export function InputBar({ onSend, disabled }: Props) {
  const handleDiceRoll = (die: string) => {
    onSend(`Roll a ${die}`);
  };

  return (
    <div className="input-bar">
      <DiceButtons onRoll={handleDiceRoll} disabled={disabled} />
      <MessageInput onSend={onSend} disabled={disabled} />
    </div>
  );
}
