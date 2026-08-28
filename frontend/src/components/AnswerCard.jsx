import CypherPreview from './CypherPreview.jsx'
import GraphView from './GraphView.jsx'
import ResultTable from './ResultTable.jsx'

export default function AnswerCard({ turn }) {
  const { question, status, data, error } = turn

  return (
    <article className="answer-card">
      <div className="question-row">
        <span className="prompt-mark mono">?</span>
        <p className="question-text">{question}</p>
      </div>

      {status === 'loading' && (
        <div className="answer-loading mono">
          <span className="pulse-dot" /> tracing a path through the graph…
        </div>
      )}

      {status === 'error' && (
        <div className="answer-error">
          <strong>That query didn't go through.</strong>
          <p>{error}</p>
        </div>
      )}

      {status === 'done' && (
        <div className="answer-body">
          <p className="explanation">{data.explanation || 'Here is what the graph returned.'}</p>
          <CypherPreview cypher={data.cypher} />
          {data.rows?.length > 0 && (
            <div className="answer-panels">
              {data.graph && data.graph.nodes?.length > 0 && (
                <GraphView graph={data.graph} />
              )}
              <ResultTable rows={data.rows} />
            </div>
          )}
          {(!data.rows || data.rows.length === 0) && (
            <div className="table-empty mono">No matches — try rephrasing, or check the name/spelling.</div>
          )}
        </div>
      )}
    </article>
  )
}
