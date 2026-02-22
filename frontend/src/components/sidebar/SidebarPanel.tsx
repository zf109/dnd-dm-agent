import { useEffect, useState } from 'react';
import { ResizablePanels } from '../layout/ResizablePanels';
import type { CharacterData } from '../../types/messages';

// ---- Character stats section ----

interface StatsProps {
  character: CharacterData | null;
  onOpenSheet: () => void;
}

function CharacterStats({ character, onOpenSheet }: StatsProps) {
  const hpPct = character && character.hp_max > 0
    ? Math.max(0, Math.min(100, (character.hp_current / character.hp_max) * 100))
    : 0;
  const hpColor = hpPct > 50 ? '#2d6a2d' : hpPct > 25 ? '#8b6914' : '#8b2020';

  return (
    <div className="sidebar-stats-section">
      <div className="sidebar-section-title">Character</div>

      {!character ? (
        <div className="no-character">No character loaded.<br />Start a campaign to begin.</div>
      ) : (
        <div className="sidebar-stats-body" onClick={onOpenSheet} title="Click to view full character sheet">
          <div className="char-name">{character.name}</div>
          <div className="char-meta">{character.classLevel} · {character.race}</div>

          <div className="hp-container">
            <div className="hp-label">
              <span>HP</span>
              <span>{character.hp_current} / {character.hp_max}</span>
            </div>
            <div className="hp-bar-track">
              <div className="hp-bar-fill" style={{ width: `${hpPct}%`, background: hpColor }} />
            </div>
          </div>

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
              <div className="sidebar-section-title" style={{ marginBottom: 6 }}>Spell Slots</div>
              <div className="spell-slot-row">
                {Array.from({ length: character.spell_slots_total }, (_, i) => (
                  <div key={i} className={`spell-pip ${i < character.spell_slots_used ? 'used' : 'available'}`} />
                ))}
              </div>
            </div>
          )}

          {character.conditions.length > 0 && (
            <div>
              <div className="sidebar-section-title" style={{ marginBottom: 6 }}>Conditions</div>
              <div className="condition-list">
                {character.conditions.map((c) => (
                  <span key={c} className="condition-badge">{c}</span>
                ))}
              </div>
            </div>
          )}

          <div className="sidebar-sheet-hint">Click to view full sheet</div>
        </div>
      )}
    </div>
  );
}

// ---- Character list section ----

interface ListProps {
  campaign: string;
  activeCharacter: string;
  onSelect: (name: string) => void;
}

function CharacterList({ campaign, activeCharacter, onSelect }: ListProps) {
  const [characters, setCharacters] = useState<string[]>([]);

  useEffect(() => {
    if (!campaign) return;
    fetch(`/api/campaigns/${campaign}/characters`)
      .then((r) => r.json())
      .then((data) => setCharacters(data.characters ?? []))
      .catch(() => {});
  }, [campaign]);

  return (
    <div className="sidebar-list-section">
      <div className="sidebar-section-title">Characters</div>
      {characters.length === 0 ? (
        <div className="no-character">No characters found</div>
      ) : (
        <ul className="character-list">
          {characters.map((name) => (
            <li
              key={name}
              className={`character-list-item ${name === activeCharacter ? 'active' : ''}`}
              onClick={() => onSelect(name)}
            >
              {name.replace(/_/g, ' ')}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ---- Combined sidebar panel ----

interface SidebarPanelProps {
  character: CharacterData | null;
  campaign: string;
  activeCharacter: string;
  onOpenSheet: () => void;
  onSelectCharacter: (name: string) => void;
}

export function SidebarPanel({ character, campaign, activeCharacter, onOpenSheet, onSelectCharacter }: SidebarPanelProps) {
  return (
    <aside className="character-sidebar">
      <ResizablePanels
        top={<CharacterStats character={character} onOpenSheet={onOpenSheet} />}
        bottom={<CharacterList campaign={campaign} activeCharacter={activeCharacter} onSelect={onSelectCharacter} />}
        initialTopPct={65}
      />
    </aside>
  );
}
