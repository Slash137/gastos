export default function Card({ title, value, hint }) {
  return (
    <div className="card">
      <p style={{ margin: '0 0 8px', color: '#64748b', fontWeight: 600 }}>{title}</p>
      <div style={{ fontSize: '1.8rem', fontWeight: 700 }}>{value}</div>
      {hint && <small style={{ color: '#94a3b8' }}>{hint}</small>}
    </div>
  )
}
