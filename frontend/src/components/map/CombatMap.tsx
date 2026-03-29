import type { Token, TerrainFeature } from './MapPanel';

const CELL = 40;

function tokenEmoji(token: Token): string {
  if (token.conditions.includes('dead')) return '💀';
  return token.type === 'party' ? '⚔️' : '🐀';
}

interface CombatMapProps {
  grid?: { width: number; height: number };
  terrain: TerrainFeature[];
  tokens: Record<string, Token>;
  current_turn?: string;
  round?: number;
}

export function CombatMap({ grid, terrain, tokens, current_turn, round }: CombatMapProps) {
  const tokenList = Object.entries(tokens);

  // Derive grid size from token positions when grid is absent
  const cols = grid?.width ?? (tokenList.length > 0
    ? Math.max(...tokenList.map(([, t]) => t.x ?? 0)) + 3
    : 10);
  const rows = grid?.height ?? (tokenList.length > 0
    ? Math.max(...tokenList.map(([, t]) => t.y ?? 0)) + 3
    : 8);

  // Tokens without positions get placed along the top row in order
  let autoX = 0;
  const placed = tokenList.map(([name, token]) => {
    if (token.x !== undefined && token.y !== undefined) {
      return { name, token, px: token.x, py: token.y };
    }
    return { name, token, px: autoX++, py: 0 };
  });

  const W = cols * CELL;
  const H = rows * CELL;

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      className="combat-map"
      preserveAspectRatio="xMidYMid meet"
      width="100%"
    >
      {/* floor */}
      <rect width={W} height={H} fill="#1c1a17" />

      {/* grid lines */}
      <g stroke="#252220" strokeWidth={0.5} opacity={0.7}>
        {Array.from({ length: cols + 1 }, (_, i) => (
          <line key={`v${i}`} x1={i * CELL} y1={0} x2={i * CELL} y2={H} />
        ))}
        {Array.from({ length: rows + 1 }, (_, i) => (
          <line key={`h${i}`} x1={0} y1={i * CELL} x2={W} y2={i * CELL} />
        ))}
      </g>

      {/* terrain */}
      {terrain.map((t, i) => {
        const stableKey = `${t.type}-${t.x ?? t.x1 ?? i}-${t.y ?? t.y1 ?? i}`;
        if (t.type === 'wall' && t.x1 !== undefined) {
          return (
            <line key={stableKey}
              x1={t.x1 * CELL} y1={(t.y1 ?? 0) * CELL}
              x2={(t.x2 ?? 0) * CELL} y2={(t.y2 ?? 0) * CELL}
              stroke="#5a4828" strokeWidth={6} strokeLinecap="round"
            />
          );
        }
        if (t.x !== undefined) {
          return (
            <g key={stableKey}>
              <rect
                x={t.x * CELL + 4} y={(t.y ?? 0) * CELL + 4}
                width={CELL - 8} height={CELL - 8} rx={3}
                fill="#2e2416" stroke="#5a4828" strokeWidth={1.5}
              />
              {t.label && (
                <text
                  x={t.x * CELL + CELL / 2}
                  y={(t.y ?? 0) * CELL + CELL / 2 + 4}
                  textAnchor="middle"
                  fontSize={7}
                  fill="#8a7050"
                  fontFamily="Georgia, serif"
                >
                  {t.label}
                </text>
              )}
            </g>
          );
        }
        return null;
      })}

      {/* tokens */}
      {placed.map(({ name, token, px, py }) => {
        const cx = px * CELL + CELL / 2;
        const cy = py * CELL + CELL / 2;
        const r = 16;
        const isDead = token.conditions.includes('dead');
        const isActive = name === current_turn;
        const hpFrac = token.max_hp > 0 ? Math.max(0, Math.min(1, token.hp / token.max_hp)) : 0;
        const hpColor = hpFrac > 0.5 ? '#3a7aaa' : hpFrac > 0.25 ? '#aa7030' : '#aa3020';
        const fill = isDead ? '#2a2420' : token.type === 'party' ? '#1e4a6a' : '#4a1a12';
        const stroke = isDead ? '#3a3630' : token.type === 'party' ? '#4a8ab0' : '#c05040';

        return (
          <g key={name}>
            {isActive && !isDead && (
              <circle cx={cx} cy={cy} r={r + 5} fill="none" stroke="#c9a84c" strokeWidth={2} opacity={0.6} />
            )}
            <circle cx={cx} cy={cy} r={r} fill={fill} stroke={stroke} strokeWidth={1.5} />
            <text x={cx} y={cy + 5} textAnchor="middle" fontSize={14}>{tokenEmoji(token)}</text>
            {!isDead && (
              <>
                <rect x={cx - r} y={cy + r + 3} width={r * 2} height={4} rx={2} fill="#141210" />
                <rect x={cx - r} y={cy + r + 3} width={r * 2 * hpFrac} height={4} rx={2} fill={hpColor} />
              </>
            )}
            <text x={cx} y={cy + r + 16} textAnchor="middle" fontSize={8}
              fill={isDead ? '#4a4440' : stroke} fontFamily="Georgia, serif">
              {name}
            </text>
          </g>
        );
      })}

      {round !== undefined && (
        <text x={W - 6} y={14} textAnchor="end" fill="#4a4040" fontSize={9} fontFamily="Georgia, serif">
          Round {round}
        </text>
      )}
    </svg>
  );
}
