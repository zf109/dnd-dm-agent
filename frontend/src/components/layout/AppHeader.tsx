import type { WSStatus } from '../../hooks/useWebSocket';

interface Props {
  campaign: string;
  wsStatus: WSStatus;
  onLeave: () => void;
}

export function AppHeader({ campaign, wsStatus, onLeave }: Props) {
  return (
    <header className="app-header">
      <h1>⚔ D&D DM Agent</h1>
      <div className="header-meta">
        {campaign && <span>{campaign}</span>}
        <div className="ws-status">
          <div className={`ws-dot ${wsStatus}`} />
          <span>{wsStatus}</span>
        </div>
        <button className="leave-btn" onClick={onLeave} title="Return to campaign selection">Leave</button>
      </div>
    </header>
  );
}
