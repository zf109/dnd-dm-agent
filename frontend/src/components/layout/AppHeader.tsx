import type { WSStatus } from '../../hooks/useWebSocket';

interface Props {
  campaign: string;
  wsStatus: WSStatus;
}

export function AppHeader({ campaign, wsStatus }: Props) {
  return (
    <header className="app-header">
      <h1>⚔ D&D DM Agent</h1>
      <div className="header-meta">
        {campaign && <span>{campaign}</span>}
        <div className="ws-status">
          <div className={`ws-dot ${wsStatus}`} />
          <span>{wsStatus}</span>
        </div>
      </div>
    </header>
  );
}
