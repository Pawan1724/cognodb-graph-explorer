function formatCell(value) {
  if (value === null || value === undefined) return '—'
  if (Array.isArray(value)) return value.map(formatCell).join(' → ')
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

export default function ResultTable({ rows }) {
  if (!rows || rows.length === 0) {
    return <div className="table-empty mono">No rows matched.</div>
  }

  const columns = Object.keys(rows[0])

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {columns.map((c) => (
                <td key={c}>{formatCell(row[c])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
