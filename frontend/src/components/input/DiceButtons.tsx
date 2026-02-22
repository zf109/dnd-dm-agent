interface Props {
  onRoll: (die: string) => void;
  disabled: boolean;
}

const DICE = ['d4', 'd6', 'd8', 'd10', 'd12', 'd20'];

export function DiceButtons({ onRoll, disabled }: Props) {
  return (
    <div className="dice-buttons">
      {DICE.map((d) => (
        <button key={d} className="dice-btn" onClick={() => onRoll(d)} disabled={disabled}>
          {d}
        </button>
      ))}
    </div>
  );
}
