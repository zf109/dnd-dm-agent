import type { CharacterData } from '../../types/messages';

interface Props {
  character: CharacterData | null;
}

function HpBar({ current, max }: { current: number; max: number }) {
  const pct = max > 0 ? Math.max(0, Math.min(100, (current / max) * 100)) : 0;
  const color = pct > 50 ? '#2d6a2d' : pct > 25 ? '#8b6914' : '#8b2020';
  return (
    <div className="hp-container">
      <div className="hp-label">
        <span>HP</span>
        <span>{current} / {max}</span>
      </div>
      <div className="hp-bar-track">
        <div className="hp-bar-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}

export function CharacterSidebar({ character }: Props) {
  return (
    <aside className="character-sidebar">
      <div className="sidebar-title">Character</div>
      {!character ? (
        <div className="no-character">
          No character loaded.<br />Start a campaign to begin.
        </div>
      ) : (
        <>
          <div>
            <div className="char-name">{character.name}</div>
            <div className="char-meta">{character.classLevel} · {character.race}</div>
          </div>

          <HpBar current={character.hp_current} max={character.hp_max} />

          <div className="stat-grid">
            <div className="stat-box">
              <div className="stat-value">{character.ac}</div>
              <div className="stat-label">AC</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">{character.speed}</div>
              <div className="stat-label">Speed</div>
            </div>
          </div>

          {character.spell_slots_total > 0 && (
            <div>
              <div className="sidebar-title" style={{ marginBottom: 6 }}>Spell Slots</div>
              <div className="spell-slot-row">
                {Array.from({ length: character.spell_slots_total }, (_, i) => (
                  <div
                    key={i}
                    className={`spell-pip ${i < character.spell_slots_used ? 'used' : 'available'}`}
                  />
                ))}
              </div>
            </div>
          )}

          {character.conditions.length > 0 && (
            <div>
              <div className="sidebar-title" style={{ marginBottom: 6 }}>Conditions</div>
              <div className="condition-list">
                {character.conditions.map((c) => (
                  <span key={c} className="condition-badge">{c}</span>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </aside>
  );
}
