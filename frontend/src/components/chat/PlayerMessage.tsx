interface Props { content: string; }

export function PlayerMessage({ content }: Props) {
  return <div className="player-message">{content}</div>;
}
