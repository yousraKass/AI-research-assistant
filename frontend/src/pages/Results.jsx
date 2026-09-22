import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Spinner, Button } from 'react-bootstrap'
import useResearchJob from '../hooks/useResearchJob'
import PipelineStatus from '../components/PipelineStatus'
import ClusterSection from '../components/ClusterSection'
import GapsSection from '../components/GapsSection'
import ReferenceList from '../components/ReferenceList'
import ErrorBanner from '../components/ErrorBanner'

export default function Results() {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const { status, stage, result, error, startPolling } = useResearchJob(jobId)

  useEffect(() => {
    if (jobId) startPolling(jobId)
  }, [jobId, startPolling])

  if (error) {
    return <ErrorBanner message={error} onBack={() => navigate('/')} />
  }

  if (!status || status === 'pending' || status === 'running') {
    return (
      <div className="mt-3">
        <PipelineStatus activeStage={stage} />
        <div className="text-center mt-4">
          <Spinner animation="border" role="status" aria-hidden="true" />
          <div className="mt-2">Working: {stage || 'initializing'}</div>
          <div className="mt-3">
            <Button variant="link" onClick={() => navigate('/')}>Cancel and go back</Button>
          </div>
        </div>
      </div>
    )
  }

  if (status === 'error') {
    return <ErrorBanner message={error || 'Unknown error'} onBack={() => navigate('/')} />
  }

  // status === done
  return (
    <div className="document-view mt-3">
      <PipelineStatus activeStage={stage} />

      {result?.overview && (
        <section className="my-4">
          <h2>Overview</h2>
          <p className="serif-content">{result.overview}</p>
        </section>
      )}

      {result?.clusters?.map((cluster, idx) => (
        <ClusterSection key={idx} cluster={cluster} />
      ))}

      {result?.gaps && result.gaps.length > 0 && (
        <GapsSection gaps={result.gaps} />
      )}

      {result?.references && (
        <ReferenceList references={result.references} />
      )}
    </div>
  )
}
