import { useEffect, useState } from 'react';
import { ExplorationMap } from './ExplorationMap';
import { CombatMap } from './CombatMap';
import './MapPanel.css';

// ── Types ────────────────────────────────────────────────────────────────────

export interface MapNode {
  id: string;
  label: string;
  visited: boolean;
}

export interface MapEdge {
  from: string;
  to: string;
}

export interface MapGraph {
  nodes: MapNode[];
  edges: MapEdge[];
  party_location: string;
}

export interface Token {
  name: string;
  x?: number;
  y?: number;
  hp: number;
  max_hp: number;
  ac?: number;
  conditions: string[];
  type: 'party' | 'enemy';
}

export interface TerrainFeature {
  type: 'wall' | 'obstacle' | 'difficult_terrain';
  label?: string;
  x?: number;
  y?: number;
  x1?: number;
  y1?: number;
  x2?: number;
  y2?: number;
}

// Raw shape as returned by the server (before normalisation)
interface RawMapState {
  mode: 'exploration' | 'combat' | null;
  room?: string;
  graph?: MapGraph;
  grid?: { width: number; height: number };
  terrain?: TerrainFeature[];
  // bookkeeping writes an array; older format may be Record
  tokens?: Token[] | Record<string, Token>;
  // bookkeeping writes [{name, roll}]; older format may be string[]
  initiative?: Array<{ name: string; roll: number }> | string[];
  // bookkeeping writes numeric index into initiative; resolved to name below
  current_turn?: string | number;
  round?: number;
}

export interface MapState {
  mode: 'exploration' | 'combat' | null;
  room?: string;
  graph?: MapGraph;
  grid?: { width: number; height: number };
  terrain?: TerrainFeature[];
  tokens: Record<string, Token>;
  current_turn?: string;
  round?: number;
}

function normalise(raw: RawMapState): MapState {
  // Normalise tokens: array → Record keyed by name
  let tokens: Record<string, Token>;
  if (Array.isArray(raw.tokens)) {
    tokens = Object.fromEntries(raw.tokens.map((t) => [t.name, t]));
  } else {
    tokens = (raw.tokens ?? {}) as Record<string, Token>;
  }

  // Normalise current_turn: numeric index → name string
  let current_turn: string | undefined;
  if (typeof raw.current_turn === 'number' && Array.isArray(raw.initiative)) {
    const entry = raw.initiative[raw.current_turn];
    current_turn = entry ? (typeof entry === 'string' ? entry : entry.name) : undefined;
  } else {
    current_turn = raw.current_turn as string | undefined;
  }

  return { ...raw, tokens, current_turn };
}

// ── Component ────────────────────────────────────────────────────────────────

interface MapPanelProps {
  instance: string;
}

export function MapPanel({ instance }: MapPanelProps) {
  const [mapData, setMapData] = useState<MapState | null>(null);

  useEffect(() => {
    let cancelled = false;

    const poll = async () => {
      try {
        const res = await fetch(`/api/map/${instance}`);
        if (res.ok && !cancelled) {
          setMapData(normalise(await res.json() as RawMapState));
        }
      } catch { /* network error — silently ignore */ }
    };

    poll();
    const id = setInterval(poll, 3000);
    return () => { cancelled = true; clearInterval(id); };
  }, [instance]);

  if (!mapData || !mapData.mode) {
    return (
      <div className="map-panel map-panel--empty">
        <span className="map-panel__placeholder-text">Map</span>
      </div>
    );
  }

  if (mapData.mode === 'exploration' && mapData.graph) {
    return (
      <div className="map-panel">
        <ExplorationMap graph={mapData.graph} />
      </div>
    );
  }

  return (
    <div className="map-panel">
      <CombatMap
        grid={mapData.grid}
        terrain={mapData.terrain ?? []}
        tokens={mapData.tokens ?? {}}
        current_turn={mapData.current_turn}
        round={mapData.round}
      />
    </div>
  );
}
