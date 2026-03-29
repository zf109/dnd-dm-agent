import type { MapGraph, MapNode } from './MapPanel';

const NODE_W = 140;
const NODE_H = 44;
const GAP_X = 24;
const GAP_Y = 36;
const COLS = 3;
const PAD = 16;

interface LayoutNode extends MapNode {
  cx: number;
  cy: number;
}

function layoutNodes(nodes: MapNode[]): LayoutNode[] {
  return nodes.map((n, i) => ({
    ...n,
    cx: PAD + (i % COLS) * (NODE_W + GAP_X) + NODE_W / 2,
    cy: PAD + Math.floor(i / COLS) * (NODE_H + GAP_Y) + NODE_H / 2,
  }));
}

interface ExplorationMapProps {
  graph: MapGraph;
}

export function ExplorationMap({ graph }: ExplorationMapProps) {
  if (graph.nodes.length === 0) {
    return (
      <svg viewBox="0 0 100 40" width="100%" className="exploration-map" preserveAspectRatio="xMidYMid meet">
        <text x={50} y={24} textAnchor="middle" fill="#4a4438" fontSize={10} fontFamily="Georgia, serif">
          No locations yet
        </text>
      </svg>
    );
  }

  const laid = layoutNodes(graph.nodes);
  const byId = Object.fromEntries(laid.map((n) => [n.id, n]));

  const cols = Math.min(graph.nodes.length, COLS);
  const rows = Math.ceil(graph.nodes.length / COLS);
  const svgW = cols * (NODE_W + GAP_X) + PAD * 2 - GAP_X;
  const svgH = rows * (NODE_H + GAP_Y) + PAD * 2 - GAP_Y;

  return (
    <svg
      viewBox={`0 0 ${svgW} ${svgH}`}
      className="exploration-map"
      preserveAspectRatio="xMidYMid meet"
      width="100%"
    >
      {/* edges */}
      {graph.edges.map((e, i) => {
        const from = byId[e.from];
        const to = byId[e.to];
        if (!from || !to) return null;
        return (
          <line
            key={`${e.from}-${e.to}`}
            x1={from.cx} y1={from.cy}
            x2={to.cx} y2={to.cy}
            stroke="#3a3228"
            strokeWidth={1.5}
            strokeDasharray="4 3"
          />
        );
      })}

      {/* nodes */}
      {laid.map((n) => {
        const isParty = n.id === graph.party_location;
        return (
          <g key={n.id}>
            <rect
              x={n.cx - NODE_W / 2}
              y={n.cy - NODE_H / 2}
              width={NODE_W}
              height={NODE_H}
              rx={5}
              fill={isParty ? '#1e2e12' : n.visited ? '#2a2418' : '#1a1814'}
              stroke={isParty ? '#4a7a28' : n.visited ? '#5a4a28' : '#3a3228'}
              strokeWidth={isParty ? 2 : 1.5}
              strokeDasharray={n.visited ? undefined : '4 3'}
            />
            <text
              x={n.cx}
              y={n.cy - (isParty ? 6 : 2)}
              textAnchor="middle"
              fill={isParty ? '#e8e0d0' : n.visited ? '#c9a84c' : '#4a4438'}
              fontSize={11}
              fontFamily="Georgia, serif"
            >
              {n.label}
            </text>
            {isParty && (
              <text
                x={n.cx}
                y={n.cy + 12}
                textAnchor="middle"
                fill="#7aaa4a"
                fontSize={9}
                fontFamily="Georgia, serif"
              >
                ● party here
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}
