import { useRef, useState, useCallback, type ReactNode } from 'react';

interface Props {
  top: ReactNode;
  bottom: ReactNode;
  initialTopPct?: number; // 0–100, default 55
}

export function ResizablePanels({ top, bottom, initialTopPct = 55 }: Props) {
  const [topPct, setTopPct] = useState(initialTopPct);
  const containerRef = useRef<HTMLDivElement>(null);

  const onDividerMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    document.body.style.cursor = 'row-resize';
    document.body.style.userSelect = 'none';

    const onMouseMove = (ev: MouseEvent) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const pct = ((ev.clientY - rect.top) / rect.height) * 100;
      setTopPct(Math.min(80, Math.max(15, pct)));
    };

    const onMouseUp = () => {
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  }, []);

  return (
    <div ref={containerRef} className="resizable-panels">
      <div className="resizable-top" style={{ height: `${topPct}%` }}>
        {top}
      </div>
      <div className="resizable-divider" onMouseDown={onDividerMouseDown}>
        <div className="resizable-divider-grip" />
      </div>
      <div className="resizable-bottom">
        {bottom}
      </div>
    </div>
  );
}
