export default function GapsSection({ gaps }) {
  return (
    <section className="gaps-section my-4 p-3" aria-labelledby="gaps-heading">
      <h3 id="gaps-heading">Gaps identified</h3>
      <ul>
        {gaps.map((g, i) => (
          <li key={i} className="serif-content">{g}</li>
        ))}
      </ul>
    </section>
  )
}
