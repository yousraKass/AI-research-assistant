import { Accordion, Button } from 'react-bootstrap'

export default function PaperDetail({ eventKey, paper }) {
  const header = `${paper.title} — ${paper.authors?.slice(0,3).join(', ')}${paper.year ? ' • ' + paper.year : ''}`

  return (
    <Accordion.Item eventKey={eventKey}>
      <Accordion.Header>{header}</Accordion.Header>
      <Accordion.Body>
        <p className="serif-content"><strong>Method:</strong> {paper.method}</p>
        <p className="serif-content"><strong>Key finding:</strong> {paper.key_finding}</p>
        <p className="serif-content"><strong>Limitation:</strong> {paper.limitation}</p>
        {paper.url && (
          <p><Button variant="link" href={paper.url} target="_blank" rel="noopener">Open paper</Button></p>
        )}
      </Accordion.Body>
    </Accordion.Item>
  )
}
