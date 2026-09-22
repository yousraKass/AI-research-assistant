import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Row, Col, Container } from 'react-bootstrap'
import SearchBar from '../components/SearchBar'
import ExampleChip from '../components/ExampleChip'
import client from '../api/client'

const EXAMPLES = [
  'RL for code generation',
  'token optimization in LLM inference',
  'agentic AI planning',
]

export default function Home() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const submit = async (q) => {
    const qtext = q || query
    if (!qtext) return
    setLoading(true)
    try {
      const resp = await client.startResearch(qtext)
      const id = resp.job_id || resp.jobId || resp.id
      navigate(`/results/${id}`)
    } catch (err) {
      // navigate to results with an error state could be handled there
      console.error(err)
      alert('Failed to start research: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container className="mt-4">
      <Row className="justify-content-center">
        <Col lg={8} md={10} sm={12}>
          <h1 className="display-6">AI Research Assistant</h1>
          <p className="lead">Turn a research question into an ordered set of relevant papers and a structured literature review.</p>
          <SearchBar value={query} onChange={setQuery} onSubmit={() => submit(query)} loading={loading} />

          <div className="mt-3">
            {EXAMPLES.map((ex) => (
              <ExampleChip key={ex} label={ex} onClick={() => { setQuery(ex); submit(ex); }} />
            ))}
          </div>
        </Col>
      </Row>
    </Container>
  )
}
