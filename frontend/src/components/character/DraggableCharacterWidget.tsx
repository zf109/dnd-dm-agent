import { useRef, useState, useCallback } from 'react';
import type { CharacterData } from '../../types/messages';

interface Props {
  character: CharacterData | null;
  onOpenSheet: () => void;
}

export function DraggableCharacterWidget({ character, onOpenSheet }: Props) {
  const [pos, setPos] = useState({ x: 16, y: 16 });
  const dragging = useRef(false);
  const dragOffset = useRef({ x: 0, y: 0 });

  const onDragMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    dragging.current = true;
    dragOffset.current = { x: e.clientX - pos.x, y: e.clientY - pos.y };
    document.body.style.userSelect = 'none';

    const onMouseMove = (ev: MouseEvent) => {
      if (!dragging.current) return;
      setPos({ x: ev.clientX - dragOffset.current.x, y: ev.clientY - dragOffset.current.y });
    };

    const onMouseUp = () => {
      dragging.current = false;
      document.body.style.userSelect = '';
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  }, [pos]);

  const hpPct = character && character.hp_max > 0
    ? Math.max(0, Math.min(100, (character.hp_current / character.hp_max) * 100))
    : 0;
  const hpColor = hpPct > 50 ? '#2d6a2d' : hpPct > 25 ? '#8b6914' : '#8b2020';

  return (
    <div className="char-widget" style={{ left: pos.x, top: pos.y }}>
      {/* Drag handle */}
      <div className="char-widget-handle" onMouseDown={onDragMouseDown}>
        <span className="char-widget-handle-label">⚔ Character</span>
        <span className="char-widget-handle-grip">⠿</span>
      </div>

      {/* Stats body — click opens full sheet */}
      <div className="char-widget-body" onClick={onOpenSheet} title="Click to view full character sheet">
        {!character ? (
          <div className="char-widget-empty">No character loaded</div>
        ) : (
          <>
            <div className="char-widget-name">{character.name}</div>
            <div className="char-widget-meta">{character.classLevel}</div>

            <div className="char-widget-hp">
              <div className="char-widget-hp-label">
                <span>HP</span>
                <span>{character.hp_current} / {character.hp_max}</span>
              </div>
              <div className="char-widget-hp-track">
                <div className="char-widget-hp-fill" style={{ width: `${hpPct}%`, background: hpColor }} />
              </div>
            </div>

            <div className="char-widget-stats">
              <div className="char-widget-stat">
                <span className="char-widget-stat-val">{character.ac}</span>
                <span className="char-widget-stat-lbl">AC</span>
              </div>
              <div className="char-widget-stat">
                <span className="char-widget-stat-val">{character.speed}</span>
                <span className="char-widget-stat-lbl">Spd</span>
              </div>
              {character.spell_slots_total > 0 && (
                <div className="char-widget-stat">
                  <span className="char-widget-stat-val">
                    {character.spell_slots_total - character.spell_slots_used}/{character.spell_slots_total}
                  </span>
                  <span className="char-widget-stat-lbl">Slots</span>
                </div>
              )}
            </div>

            {character.conditions.length > 0 && (
              <div className="char-widget-conditions">
                {character.conditions.map((c) => (
                  <span key={c} className="condition-badge">{c}</span>
                ))}
              </div>
            )}

            <div className="char-widget-hint">Click to view full sheet</div>
          </>
        )}
      </div>
    </div>
  );
}
