import { Row, Col } from 'react-bootstrap'

export default function About() {
  return (
    <Row className="mt-3">
      <Col lg={8} md={10}>
        <h1>About</h1>
        <p>This tool converts a research question into an ordered set of relevant papers and a structured literature review, helping researchers do a fast, first-pass survey over large literatures.</p>

        <h2>Pipeline</h2>
        <div className="pipeline-steps d-flex flex-column flex-sm-row gap-2">
          <div className="step">search</div>
          <div className="step">summarize</div>
          <div className="step">cluster</div>
          <div className="step">identify gaps</div>
          <div className="step">synthesize</div>
        </div>

        <p className="mt-3">Source code: <a href="https://github.com/placeholder/repo">GitHub repository</a></p>
      </Col>
    </Row>
  )
}
