import { useState } from 'react'

export default function CypherPreview({ cypher }) {
  const [open, setOpen] = useState(false)

  if (!cypher) return null

  return (
    <div className="cypher-preview">
      <button className="cypher-toggle mono" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        <span className="cypher-dot" aria-hidden="true" />
        {open ? 'hide the cypher query' : 'show the cypher query'}
      </button>
      {open && (
        <pre className="cypher-body mono">
          <code>{cypher}</code>
        </pre>
      )}
    </div>
  )
}
