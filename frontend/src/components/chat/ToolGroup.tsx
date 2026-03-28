import { useState } from 'react';

interface Tool {
  display: string;
  tooltip: string;
  source: 'dm' | 'bookkeeping';
}

interface Props {
  tools: Tool[];
  isComplete: boolean;
}

function ToolStep({ tool, isActive }: { tool: Tool; isActive: boolean }) {
  const title = [tool.tooltip, tool.source === 'bookkeeping' ? '(bookkeeping)' : ''].filter(Boolean).join(' ');
  return (
    <div className={`tool-step ${isActive ? 'active' : 'done'}`} title={title || undefined}>
      {isActive ? <div className="tool-spinner" /> : <span className="tool-step-icon">✓</span>}
      <span>{tool.display}{isActive ? '...' : ''}</span>
    </div>
  );
}

export function ToolGroup({ tools, isComplete }: Props) {
  const [expanded, setExpanded] = useState(false);

  if (!isComplete) {
    return (
      <div className="tool-group">
        {tools.map((tool, i) => (
          <ToolStep key={i} tool={tool} isActive={i === tools.length - 1} />
        ))}
      </div>
    );
  }

  return (
    <div className="tool-group complete">
      <button className="tool-group-summary" onClick={() => setExpanded(x => !x)}>
        <span className="tool-step-icon">✓</span>
        <span>Used {tools.length} tool{tools.length !== 1 ? 's' : ''}</span>
        <span className="tool-group-chevron">{expanded ? '▴' : '▾'}</span>
      </button>
      {expanded && (
        <div className="tool-group-expanded">
          {tools.map((tool, i) => (
            <ToolStep key={i} tool={tool} isActive={false} />
          ))}
        </div>
      )}
    </div>
  );
}
