import { Alert, Button } from 'react-bootstrap'

export default function ErrorBanner({ message, onBack }) {
  return (
    <Alert variant="danger" className="mt-3">
      <Alert.Heading>Something went wrong</Alert.Heading>
      <p>{message}</p>
      <div className="d-flex justify-content-end">
        <Button onClick={onBack} variant="secondary">Back</Button>
      </div>
    </Alert>
  )
}
