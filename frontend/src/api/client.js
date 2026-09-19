const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function startResearch(query) {
  const res = await fetch(`${API_BASE}/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
  if (!res.ok) throw new Error(`Failed to start research (${res.status})`)
  return res.json()
}

export async function getResearch(jobId) {
  const res = await fetch(`${API_BASE}/research/${encodeURIComponent(jobId)}`)
  if (!res.ok) throw new Error(`Failed to fetch job ${jobId} (${res.status})`)
  return res.json()
}

export async function searchPapers(q) {
  const res = await fetch(`${API_BASE}/papers/search?q=${encodeURIComponent(q)}`)
  if (!res.ok) throw new Error(`Paper search failed (${res.status})`)
  return res.json()
}

export default { startResearch, getResearch, searchPapers }
