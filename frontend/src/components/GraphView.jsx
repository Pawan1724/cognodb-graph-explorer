const LABEL_COLOR = {
  Person: 'var(--node-employee)',
  Company: 'var(--node-team)',
  Project: 'var(--node-project)',
  Task: 'var(--node-department)',
  Meeting: 'var(--node-skill)',
  Email: 'var(--node-certification)',
}

const NODE_RADIUS = 9

function layoutLayered(nodes, width, height) {
  const groups = {};
  nodes.forEach(n => {
    const label = n.labels?.[0] || 'Unknown';
    if (!groups[label]) groups[label] = [];
    groups[label].push(n);
  });

  const labels = Object.keys(groups);
  const numCols = Math.max(labels.length, 1);
  const colWidth = width / (numCols + 1);
  
  const positioned = [];
  labels.forEach((label, colIndex) => {
    const groupNodes = groups[label];
    const numNodes = groupNodes.length;
    const x = colWidth * (colIndex + 1);
    
    const rowHeight = height / (numNodes + 1);
    groupNodes.forEach((n, rowIndex) => {
      const y = rowHeight * (rowIndex + 1);
      positioned.push({ ...n, x, y, colIndex, numCols });
    });
  });

  return positioned;
}

export default function GraphView({ graph }) {
  const width = 560
  const height = 340

  if (!graph || graph.nodes.length === 0) {
    return (
      <div className="graph-empty mono">
        This answer didn't return graph entities to visualize — see the table instead.
      </div>
    )
  }

  const positioned = layoutLayered(graph.nodes, width, height)
  const byId = Object.fromEntries(positioned.map((n) => [n.id, n]))

  return (
    <div className="graph-view">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Graph of the entities in this answer">
        {graph.links.map((l, i) => {
          const s = byId[l.source]
          const t = byId[l.target]
          if (!s || !t) return null
          const mx = (s.x + t.x) / 2
          const my = (s.y + t.y) / 2
          return (
            <g key={i}>
              <line x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke="var(--line)" strokeWidth="1.5" />
              <text x={mx} y={my - 4} className="mono link-label" textAnchor="middle">
                {l.type}
              </text>
            </g>
          )
        })}
        {positioned.map((n) => {
          const label = n.labels?.[0] || 'Node'
          const color = LABEL_COLOR[label] || 'var(--fog)'
          const name = n.properties?.name || n.properties?.title || label
          
          let textX = n.x;
          let textY = n.y;
          let anchor = 'middle';
          
          if (n.numCols > 1) {
            if (n.colIndex === 0) {
              textX = n.x - NODE_RADIUS - 8;
              anchor = 'end';
            } else if (n.colIndex === n.numCols - 1) {
              textX = n.x + NODE_RADIUS + 8;
              anchor = 'start';
            } else {
              textY = n.y + NODE_RADIUS + 14;
            }
          } else {
             textY = n.y + NODE_RADIUS + 14;
          }

          if (anchor !== 'middle') {
            textY = n.y + 3;
          }

          return (
            <g key={n.id}>
              <circle cx={n.x} cy={n.y} r={NODE_RADIUS} fill={color} stroke="var(--ink)" strokeWidth="2">
                <title>{`${label}: ${name}`}</title>
              </circle>
              <text x={textX} y={textY} textAnchor={anchor} className="node-label">
                {name}
              </text>
            </g>
          )
        })}
      </svg>
      <div className="graph-legend">
        {Object.entries(LABEL_COLOR).map(([label, color]) => (
          <span key={label} className="legend-item">
            <span className="legend-dot" style={{ background: color }} />
            {label}
          </span>
        ))}
      </div>
    </div>
  )
}
