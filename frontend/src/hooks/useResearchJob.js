import { useEffect, useRef, useState, useCallback } from 'react'
import { startResearch, getResearch } from '../api/client'

export default function useResearchJob(initialJobId = null) {
  const [jobId, setJobId] = useState(initialJobId)
  const [status, setStatus] = useState(null)
  const [stage, setStage] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const pollingRef = useRef(null)

  const pollOnce = useCallback(async (id) => {
    try {
      const data = await getResearch(id)
      setStatus(data.status)
      setStage(data.stage)
      setResult(data.result)
      setError(data.error)
      return data
    } catch (err) {
      setError(err.message)
      setStatus('error')
      return null
    }
  }, [])

  const startPolling = useCallback((id) => {
    if (!id) return
    // clear any existing
    if (pollingRef.current) clearInterval(pollingRef.current)
    // initial fetch
    pollOnce(id)
    pollingRef.current = setInterval(async () => {
      const data = await pollOnce(id)
      if (!data) return
      if (data.status === 'done' || data.status === 'error') {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
    }, 2000)
  }, [pollOnce])

  useEffect(() => {
    if (initialJobId) {
      setJobId(initialJobId)
      startPolling(initialJobId)
    }
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current)
    }
  }, [initialJobId, startPolling])

  const start = useCallback(async (query) => {
    setError(null)
    try {
      const resp = await startResearch(query)
      const id = resp.job_id || resp.jobId || resp.id
      setJobId(id)
      startPolling(id)
      return id
    } catch (err) {
      setError(err.message)
      setStatus('error')
      throw err
    }
  }, [startPolling])

  const cancel = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
  }, [])

  return { jobId, status, stage, result, error, start, startPolling, cancel }
}
