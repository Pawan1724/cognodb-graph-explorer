import { useEffect, useRef, useState } from 'react'
import { api } from './api.js'
import AnswerCard from './components/AnswerCard.jsx'
import './app.css'

const EXAMPLE_QUESTIONS = [
  'Who does Diya Nair report to, all the way to the top?',
  'Which employees have the skills for Atlas Migration but aren\u2019t on it yet?',
  'What is the org-chart distance between two random engineers?',
  'What skills does the Engineering department need but nobody has?',
]

export default function App() {
  const [connection, setConnection] = useState({ state: 'checking' })
  const [question, setQuestion] = useState('')
  const [turns, setTurns] = useState([])
  const threadEndRef = useRef(null)

  useEffect(() => {
    api
      .health()
      .then((h) =>
        setConnection(
          h.status === 'ok'
            ? { state: 'connected' }
            : { state: 'down', detail: h.detail || h.problems?.join(', ') }
        )
      )
      .catch((e) => setConnection({ state: 'down', detail: e.message }))
  }, [])

  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [turns])

  async function ask(q) {
    const question = q.trim()
    if (!question) return

    const turnId = crypto.randomUUID()
    setTurns((prev) => [...prev, { id: turnId, question, status: 'loading' }])
    setQuestion('')

    try {
      const data = await api.ask(question)
      setTurns((prev) =>
        prev.map((t) => (t.id === turnId ? { ...t, status: 'done', data } : t))
      )
    } catch (e) {
      setTurns((prev) =>
        prev.map((t) => (t.id === turnId ? { ...t, status: 'error', error: e.message } : t))
      )
    }
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark display" aria-hidden="true">◈</span>
          <span className="brand-name display">OrgGraph</span>
        </div>
        <div className={`status-badge mono status-${connection.state}`}>
          <span className="status-dot" />
          {connection.state === 'checking' && 'checking database…'}
          {connection.state === 'connected' && 'graph connected'}
          {connection.state === 'down' && 'database unreachable'}
        </div>
      </header>

      {connection.state === 'down' && (
        <div className="banner-error">
          Can't reach CognoDB right now ({connection.detail}). Questions won't run until the
          connection is back — check your <code className="mono">.env</code> and that the
          instance is awake.
        </div>
      )}

      <main className="app-main">
        {turns.length === 0 && (
          <div className="empty-state">
            <h1 className="display">Ask your org anything.</h1>
            <p>
              This graph knows who reports to whom, who has which skills, and who's worked on
              what. Ask a plain-English question — it gets translated to Cypher and run live.
            </p>
            <div className="chip-row">
              {EXAMPLE_QUESTIONS.map((q) => (
                <button key={q} className="chip mono" onClick={() => ask(q)}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="thread">
          {turns.map((t) => (
            <AnswerCard key={t.id} turn={t} />
          ))}
          <div ref={threadEndRef} />
        </div>
      </main>

      <form
        className="composer"
        onSubmit={(e) => {
          e.preventDefault()
          ask(question)
        }}
      >
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. Who could staff the Recommendation Engine project?"
          aria-label="Ask a question about the org graph"
        />
        <button type="submit" className="send-btn" disabled={!question.trim()}>
          Ask
        </button>
      </form>
    </div>
  )
}
