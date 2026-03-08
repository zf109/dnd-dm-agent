interface Props { display_name: string; }

export function ToolUseEvent({ display_name }: Props) {
  return (
    <div className="tool-indicator">
      <div className="tool-spinner" />
      <span>DM is {display_name}...</span>
    </div>
  );
}
