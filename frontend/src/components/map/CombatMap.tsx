import type { Token, TerrainFeature } from './MapPanel';

export function CombatMap(_props: {
  grid?: { width: number; height: number };
  terrain: TerrainFeature[];
  tokens: Record<string, Token>;
  current_turn?: string;
  round?: number;
}) {
  return <div className="combat-map" />;
}
