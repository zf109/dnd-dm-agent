interface Props {
  notation: string;
  rolls: number[];
  total: number;
  modifier: number;
}

export function DiceRollEvent({ notation, rolls, total }: Props) {
  return (
    <div className="dice-event">
      <div className="dice-notation">{notation}</div>
      <div className="dice-rolls">
        {rolls.map((r, i) => (
          <span key={i} className="dice-roll-pip">{r}</span>
        ))}
      </div>
      <div className="dice-total">{total}</div>
    </div>
  );
}
