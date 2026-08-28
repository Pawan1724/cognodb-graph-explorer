const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function handle(res) {
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch {
      // response wasn't JSON, fall back to statusText
    }
    const error = new Error(detail)
    error.status = res.status
    throw error
  }
  return res.json()
}

/**
 * Transform raw graph_data from the backend into the format
 * expected by the frontend components.
 *
 * Backend returns: { cypher_query, graph_data, answer, ... }
 * Frontend expects: { cypher, rows, graph: {nodes, links}, explanation }
 */
function transformResponse(data) {
  const graphData = data.graph_data || data.graph || []

  // Build flattened rows for ResultTable — each record may have nested
  // objects like { proj: { name: "Apollo", ... } }, so we flatten them.
  const rows = graphData.map((record) => {
    const flat = {}
    for (const [key, value] of Object.entries(record)) {
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        // Flatten nested node properties: { proj: { name: "Apollo" } } → { name: "Apollo", ... }
        for (const [prop, val] of Object.entries(value)) {
          flat[prop] = val
        }
      } else {
        flat[key] = value
      }
    }
    return flat
  })

  return {
    cypher: data.cypher_query || data.cypher || '',
    explanation: data.answer || data.explanation || 'Here is what the graph returned.',
    rows,
    graph: data.graph_viz || null,
  }
}

export const api = {
  health: () => fetch(`${BASE_URL}/health`).then(handle),
  lookups: () => fetch(`${BASE_URL}/lookups`).then(handle),
  sampleQueries: () => fetch(`${BASE_URL}/sample-queries`).then(handle),
  runSampleQuery: (key, params) =>
    fetch(`${BASE_URL}/sample-queries/${key}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ params }),
    }).then(handle),
  ask: (question) =>
    fetch(`${BASE_URL}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    })
      .then(handle)
      .then(transformResponse),
}
