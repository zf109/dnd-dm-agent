import { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Props {
  markdown: string;
  characterName: string;
  onClose: () => void;
}

export function CharacterSheetModal({ markdown, characterName, onClose }: Props) {
  const overlayRef = useRef<HTMLDivElement>(null);

  // Close on Escape key
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  return (
    <div
      className="sheet-overlay"
      ref={overlayRef}
      onClick={(e) => { if (e.target === overlayRef.current) onClose(); }}
    >
      <div className="sheet-modal">
        <div className="sheet-modal-header">
          <h2 className="sheet-modal-title">{characterName.replace(/_/g, ' ')}</h2>
          <button className="sheet-modal-close" onClick={onClose} aria-label="Close">✕</button>
        </div>
        <div className="sheet-modal-body">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
