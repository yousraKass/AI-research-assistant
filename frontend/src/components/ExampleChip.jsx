import { Button } from 'react-bootstrap'

export default function ExampleChip({ label, onClick }) {
  return (
    <Button
      variant="outline-secondary"
      size="sm"
      className="me-2 mb-2"
      onClick={() => onClick(label)}
      aria-label={`Use example query: ${label}`}
    >
      {label}
    </Button>
  )
}
