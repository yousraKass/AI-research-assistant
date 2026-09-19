import { Form, InputGroup, Button } from 'react-bootstrap'

export default function SearchBar({ value, onChange, onSubmit, loading }) {
  return (
    <Form onSubmit={(e) => { e.preventDefault(); onSubmit(); }}>
      <label className="visually-hidden" htmlFor="research-query">Research query</label>
      <InputGroup className="mb-2 input-lg">
        <Form.Control
          id="research-query"
          size="lg"
          placeholder="Describe your research question — e.g. 'RL for code generation'"
          aria-label="Research query"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          autoComplete="off"
        />
        <Button type="submit" size="lg" variant="primary" disabled={loading} aria-disabled={loading}>
          {loading ? 'Starting...' : 'Search'}
        </Button>
      </InputGroup>
    </Form>
  )
}
