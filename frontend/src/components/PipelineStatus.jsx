import './pipeline.css'
import { useEffect, useRef } from 'react'

const STAGES = [
  { key: 'searching', label: 'searching' },
  { key: 'summarizing', label: 'summarizing' },
  { key: 'clustering', label: 'clustering' },
  { key: 'analyzing_gaps', label: 'analyzing gaps' },
  { key: 'synthesizing', label: 'synthesizing' },
]

export default function PipelineStatus({ activeStage }) {
  const liveRef = useRef(null)

  useEffect(() => {
    if (liveRef.current) {
      liveRef.current.textContent = activeStage || 'starting'
    }
  }, [activeStage])

  return (
    <div className="pipeline-status mb-3" aria-label="Pipeline status">
      <ol className="list-unstyled d-flex gap-3 flex-wrap" role="list">
        {STAGES.map((s) => (
          <li key={s.key} role="listitem" className={`stage ${s.key === activeStage ? 'active' : ''}`} aria-current={s.key === activeStage ? 'step' : undefined}>
            <div className="stage-dot" aria-hidden></div>
            <div className="stage-label">{s.label}</div>
          </li>
        ))}
      </ol>
      <div className="visually-hidden" aria-live="polite" ref={liveRef}></div>
    </div>
  )
}
