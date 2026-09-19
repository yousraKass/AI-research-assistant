import { Accordion } from 'react-bootstrap'
import PaperDetail from './PaperDetail'

export default function ClusterSection({ cluster }) {
  return (
    <section className="my-4">
      <h3>{cluster.title}</h3>
      <p className="serif-content">{cluster.summary}</p>

      <Accordion>
        {cluster.papers.map((p, idx) => (
          <PaperDetail key={idx} eventKey={String(idx)} paper={p} />
        ))}
      </Accordion>
    </section>
  )
}
