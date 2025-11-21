import { useState } from 'react'
import Layout from '../components/Layout'
import api from '../api/client'

export default function ImportPage() {
  const [file, setFile] = useState(null)
  const [summary, setSummary] = useState(null)
  const [status, setStatus] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!file) return
    setStatus('Procesando...')
    const formData = new FormData()
    formData.append('archivo', file)
    try {
      const { data } = await api.post('/import/csv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setSummary(data)
      setStatus('Importación completada')
    } catch (error) {
      setStatus('Hubo un problema al procesar el CSV')
    }
  }

  return (
    <Layout>
      <h1>Importar CSV</h1>
      <p style={{ color: '#64748b' }}>Carga extractos bancarios con columnas estandarizadas.</p>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: 12, maxWidth: 400 }}>
        <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0])} />
        <button type="submit" style={{ padding: '10px 12px', borderRadius: 8, border: 'none', background: '#0ea5e9', color: '#fff', fontWeight: 600 }}>
          Importar
        </button>
      </form>
      {status && <p>{status}</p>}
      {summary && (
        <div className="card" style={{ marginTop: 16 }}>
          <p>Filas insertadas: {summary.insertados}</p>
          {summary.errores.length > 0 && (
            <ul>
              {summary.errores.map((err) => (
                <li key={err}>{err}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </Layout>
  )
}
