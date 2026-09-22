export default function ReferenceList({ references }) {
  return (
    <section className="my-4">
      <h4>References</h4>
      <ol>
        {references.map((r, i) => (
          <li key={i} className="serif-content">
            <a href={r.url} target="_blank" rel="noopener noreferrer">{r.title}</a>
            {r.authors && ` — ${r.authors.join(', ')}`}
            {r.year && ` (${r.year})`}
          </li>
        ))}
      </ol>
    </section>
  )
}
