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
  x?: number;
  y?: number;
  hp: number;
  max_hp: number;
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

export interface MapState {
  mode: 'exploration' | 'combat' | null;
  room?: string;
  graph?: MapGraph;
  grid?: { width: number; height: number };
  terrain?: TerrainFeature[];
  tokens?: Record<string, Token>;
  initiative?: string[];
  current_turn?: string;
  round?: number;
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
          setMapData(await res.json() as MapState);
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
