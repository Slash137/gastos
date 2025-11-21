import { useEffect, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Layout from '../components/Layout'
import ImportMappingForm from '../components/ImportMappingForm'
import ImportPreviewTable from '../components/ImportPreviewTable'
import { analyzeImport, applyImport, previewImport, fetcher } from '../api/client'

export default function ImportPage() {
  const [file, setFile] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [mapping, setMapping] = useState(null)
  const [options, setOptions] = useState({
    detectar_tipo_por_signo: true,
    aplicar_reglas: true,
    ignorar_duplicados: true,
    limpiar_concepto: true
  })
  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const { data: tipos } = useQuery({ queryKey: ['tipos'], queryFn: () => fetcher('/tipos') })
  const { data: categorias } = useQuery({ queryKey: ['categorias'], queryFn: () => fetcher('/categorias') })
  const { data: metodos } = useQuery({ queryKey: ['metodos-pago'], queryFn: () => fetcher('/metodos-pago') })

  const columnasDisponibles = useMemo(() => analysis?.columns || [], [analysis])

  useEffect(() => {
    if (analysis?.suggested_mapping) {
      setMapping(analysis.suggested_mapping)
    } else if (columnasDisponibles.length && !mapping) {
      setMapping({ fecha_col: columnasDisponibles[0], concepto_col: columnasDisponibles[0] })
    }
  }, [analysis, columnasDisponibles, mapping])

  useEffect(() => {
    if (categorias?.length && !options.default_categoria_id) {
      setOptions((prev) => ({ ...prev, default_categoria_id: categorias[0].id }))
    }
    if (metodos?.length && !options.default_metodo_pago_id) {
      setOptions((prev) => ({ ...prev, default_metodo_pago_id: metodos[0].id }))
    }
  }, [categorias, metodos, options.default_categoria_id, options.default_metodo_pago_id])

  const handleAnalyze = async (evt) => {
    evt.preventDefault()
    if (!file) return
    setIsLoading(true)
    setError('')
    setPreview(null)
    setResult(null)
    try {
      const data = await analyzeImport(file)
      setAnalysis(data)
      if (data.suggested_mapping) {
        setMapping(data.suggested_mapping)
      }
    } catch (err) {
      setError('No se pudo analizar el CSV')
    } finally {
      setIsLoading(false)
    }
  }

  const handlePreview = async () => {
    if (!file || !mapping) return
    setIsLoading(true)
    setError('')
    setResult(null)
    try {
      const data = await previewImport(file, mapping, options)
      setPreview(data)
    } catch (err) {
      setError('No se pudo previsualizar el archivo')
    } finally {
      setIsLoading(false)
    }
  }

  const handleApply = async () => {
    if (!file || !mapping) return
    setIsLoading(true)
    setError('')
    try {
      const data = await applyImport(file, mapping, options)
      setResult(data)
    } catch (err) {
      setError('No se pudo completar la importación')
    } finally {
      setIsLoading(false)
    }
  }

  const updateOption = (field, value) => setOptions((prev) => ({ ...prev, [field]: value }))

  return (
    <Layout>
      <h1>Importar CSV</h1>
      <p style={{ color: '#64748b' }}>
        Asistente paso a paso para revisar, mapear y subir extractos bancarios con seguridad.
      </p>

      <form onSubmit={handleAnalyze} className="card" style={{ display: 'grid', gap: 12 }}>
        <label className="field">
          <span>Selecciona un CSV</span>
          <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0])} />
        </label>
        <button type="submit" className="primary" disabled={!file || isLoading}>
          {isLoading ? 'Analizando...' : 'Analizar'}
        </button>
        {analysis && (
          <div style={{ display: 'grid', gap: 6 }}>
            <span style={{ fontWeight: 600 }}>Formato detectado: {analysis.format}</span>
            <span style={{ color: '#64748b' }}>Columnas: {analysis.columns.join(', ')}</span>
          </div>
        )}
      </form>

      {analysis && mapping && (
        <div style={{ display: 'grid', gap: 16, marginTop: 16 }}>
          <ImportMappingForm columns={columnasDisponibles} mapping={mapping} setMapping={setMapping} />

          <div className="card" style={{ display: 'grid', gap: 10 }}>
            <div>
              <p style={{ margin: 0, fontWeight: 600 }}>Opciones</p>
              <p style={{ margin: 0, color: '#64748b' }}>Define valores por defecto y reglas de validación.</p>
            </div>
            <div className="field">
              <span>Tipo por defecto</span>
              <select
                value={options.default_tipo_id || ''}
                onChange={(e) => updateOption('default_tipo_id', Number(e.target.value) || null)}
              >
                <option value="">Según signo</option>
                {tipos?.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.nombre}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <span>Categoría por defecto</span>
              <select
                value={options.default_categoria_id || ''}
                onChange={(e) => updateOption('default_categoria_id', Number(e.target.value) || null)}
              >
                <option value="">Selecciona</option>
                {categorias?.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.nombre}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <span>Método de pago</span>
              <select
                value={options.default_metodo_pago_id || ''}
                onChange={(e) => updateOption('default_metodo_pago_id', Number(e.target.value) || null)}
              >
                <option value="">Selecciona</option>
                {metodos?.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.nombre}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <input
                  type="checkbox"
                  checked={options.detectar_tipo_por_signo}
                  onChange={(e) => updateOption('detectar_tipo_por_signo', e.target.checked)}
                />
                <span>Detectar gasto/ingreso por signo del importe</span>
              </label>
            </div>
            <div className="field">
              <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <input
                  type="checkbox"
                  checked={options.aplicar_reglas}
                  onChange={(e) => updateOption('aplicar_reglas', e.target.checked)}
                />
                <span>Aplicar reglas de categorización</span>
              </label>
            </div>
            <div className="field">
              <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <input
                  type="checkbox"
                  checked={options.ignorar_duplicados}
                  onChange={(e) => updateOption('ignorar_duplicados', e.target.checked)}
                />
                <span>Ignorar filas duplicadas detectadas</span>
              </label>
            </div>
            <div className="field">
              <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <input
                  type="checkbox"
                  checked={options.limpiar_concepto}
                  onChange={(e) => updateOption('limpiar_concepto', e.target.checked)}
                />
                <span>Normalizar espacios en concepto</span>
              </label>
            </div>
            <label className="field">
              <span>Formato de fecha (opcional)</span>
              <input
                type="text"
                value={options.formato_fecha || ''}
                placeholder="%d/%m/%Y"
                onChange={(e) => updateOption('formato_fecha', e.target.value || null)}
              />
            </label>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <button type="button" className="primary" onClick={handlePreview} disabled={isLoading}>
                {isLoading ? 'Procesando...' : 'Previsualizar'}
              </button>
              <button type="button" onClick={() => setResult(null)} disabled={isLoading}>
                Limpiar resultado
              </button>
            </div>
          </div>
        </div>
      )}

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {preview && (
        <div style={{ display: 'grid', gap: 10, marginTop: 16 }}>
          <div className="card" style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <span>Total filas: {preview.total_rows}</span>
            <span>Válidas: {preview.valid_rows}</span>
            <span>Errores: {preview.error_rows}</span>
            <span>Duplicados: {preview.duplicate_rows}</span>
          </div>
          <ImportPreviewTable rows={preview.rows} />
          <button
            type="button"
            className="primary"
            onClick={handleApply}
            disabled={isLoading || !preview.valid_rows}
          >
            {isLoading ? 'Importando...' : `Importar ${preview.valid_rows} filas válidas`}
          </button>
        </div>
      )}

      {result && (
        <div className="card" style={{ marginTop: 16 }}>
          <p style={{ margin: 0, fontWeight: 600 }}>Resultado de importación</p>
          <p style={{ margin: 0 }}>Importadas: {result.imported}</p>
          <p style={{ margin: 0 }}>Duplicados omitidos: {result.skipped_duplicates}</p>
          <p style={{ margin: 0 }}>Errores: {result.skipped_errors}</p>
        </div>
      )}
    </Layout>
  )
}

