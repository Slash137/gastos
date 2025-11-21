import { useEffect, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Layout from '../components/Layout'
import MovimientosTable from '../components/MovimientosTable'
import { serializeParams, useMovimientos } from '../hooks/useMovimientos'
import { exportMovimientosCsv, fetcher, patchMovimiento } from '../api/client'

const defaultFilters = {
  fecha_desde: '',
  fecha_hasta: '',
  categoria_ids: [],
  tipo_ids: [],
  metodo_pago_ids: [],
  importe_min: '',
  importe_max: '',
  search: '',
  solo_gastos_fijos: false,
  solo_gastos_variables: false
}

const TIPOS = [
  { id: 1, nombre: 'Gasto' },
  { id: 2, nombre: 'Ingreso' }
]

const vistasKey = 'movimientos_saved_views'

const formatDate = (date) => date.toISOString().slice(0, 10)

export default function MovimientosPage() {
  const [filters, setFilters] = useState(defaultFilters)
  const [searchInput, setSearchInput] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(50)
  const [sorting, setSorting] = useState({ id: 'fecha', desc: true })
  const [grouping, setGrouping] = useState([])
  const [savedViews, setSavedViews] = useState([])
  const [selectedRow, setSelectedRow] = useState(null)
  const [tableData, setTableData] = useState([])

  const { data, isLoading } = useMovimientos({
    ...filters,
    search: filters.search || undefined,
    page,
    page_size: pageSize,
    sort_by: sorting?.id,
    sort_dir: sorting?.desc ? 'desc' : 'asc'
  })

  useEffect(() => {
    const timeout = setTimeout(() => {
      setFilters((prev) => ({ ...prev, search: searchInput }))
      setPage(1)
    }, 400)
    return () => clearTimeout(timeout)
  }, [searchInput])

  useEffect(() => {
    const vistas = localStorage.getItem(vistasKey)
    if (vistas) setSavedViews(JSON.parse(vistas))
  }, [])

  useEffect(() => {
    if (data?.items) setTableData(data.items)
  }, [data])

  const { data: categorias } = useQuery({ queryKey: ['categorias'], queryFn: () => fetcher('/categorias') })
  const { data: metodos } = useQuery({ queryKey: ['metodos_pago'], queryFn: () => fetcher('/metodos-pago') })

  const handleDatePreset = (preset) => {
    const now = new Date()
    let desde = ''
    let hasta = formatDate(now)
    switch (preset) {
      case 'hoy':
        desde = formatDate(now)
        break
      case '7d':
        desde = formatDate(new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000))
        break
      case 'mes':
        desde = formatDate(new Date(now.getFullYear(), now.getMonth(), 1))
        break
      case 'anio':
        desde = formatDate(new Date(now.getFullYear(), 0, 1))
        break
      case '12m':
        desde = formatDate(new Date(now.getFullYear(), now.getMonth() - 11, 1))
        break
      default:
        break
    }
    setFilters((prev) => ({ ...prev, fecha_desde: desde, fecha_hasta: hasta }))
    setPage(1)
  }

  const handleApplyFilters = () => setPage(1)
  const handleClearFilters = () => {
    setFilters(defaultFilters)
    setSearchInput('')
    setPage(1)
  }

  const handleSaveView = () => {
    const name = prompt('Nombre de la vista')
    if (!name) return
    const nuevas = [...savedViews, { name, filters, sorting }]
    setSavedViews(nuevas)
    localStorage.setItem(vistasKey, JSON.stringify(nuevas))
  }

  const applyView = (vista) => {
    setFilters(vista.filters)
    setSorting(vista.sorting)
    setPage(1)
  }

  const deleteView = (name) => {
    const restantes = savedViews.filter((v) => v.name !== name)
    setSavedViews(restantes)
    localStorage.setItem(vistasKey, JSON.stringify(restantes))
  }

  const onInlineUpdate = async (id, payload) => {
    const updated = await patchMovimiento(id, payload)
    setTableData((prev) => prev.map((row) => (row.id === id ? { ...row, ...updated } : row)))
  }

  const handleExport = async () => {
    const rawPayload = {
      ...filters,
      search: filters.search || undefined,
      sort_by: sorting?.id,
      sort_dir: sorting?.desc ? 'desc' : 'asc'
    }
    const payload = Object.fromEntries(
      Object.entries(rawPayload).filter(([, value]) => value !== undefined && value !== '')
    )
    const blob = await exportMovimientosCsv(payload)
    const url = window.URL.createObjectURL(new Blob([blob]))
    const a = document.createElement('a')
    a.href = url
    a.download = 'movimientos.csv'
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const sideSummaryFilters = useMemo(() => {
    if (!selectedRow) return null
    return {
      ...filters,
      categoria_ids: selectedRow.categoria_id ? [selectedRow.categoria_id] : [],
      page: 1,
      page_size: 1
    }
  }, [filters, selectedRow])

  const { data: categoriaSummary } = useQuery({
    queryKey: ['movimientos', 'context', sideSummaryFilters],
    enabled: !!selectedRow,
    queryFn: () => {
      const { query } = serializeParams({ ...sideSummaryFilters, page: 1, page_size: 1 })
      return fetcher(`/movimientos${query ? `?${query}` : ''}`)
    }
  })

  const totalPages = data?.total_pages || 1

  return (
    <Layout>
      <div className="page-header">
        <div>
          <h1>Movimientos</h1>
          <p className="muted">Explora, agrupa y exporta movimientos con filtros avanzados.</p>
        </div>
        <div className="header-actions">
          <button className="btn" onClick={handleSaveView}>Guardar vista</button>
          <button className="btn" onClick={handleExport}>Exportar CSV</button>
        </div>
      </div>

      <section className="filters card">
        <div className="filters-row">
          <div>
            <label>Desde</label>
            <input type="date" value={filters.fecha_desde} onChange={(e) => setFilters({ ...filters, fecha_desde: e.target.value })} />
          </div>
          <div>
            <label>Hasta</label>
            <input type="date" value={filters.fecha_hasta} onChange={(e) => setFilters({ ...filters, fecha_hasta: e.target.value })} />
          </div>
          <div className="preset-buttons">
            <span>Rangos rápidos</span>
            <div className="chips">
              <button onClick={() => handleDatePreset('hoy')}>Hoy</button>
              <button onClick={() => handleDatePreset('7d')}>Últimos 7 días</button>
              <button onClick={() => handleDatePreset('mes')}>Este mes</button>
              <button onClick={() => handleDatePreset('anio')}>Año actual</button>
              <button onClick={() => handleDatePreset('12m')}>Últimos 12 meses</button>
            </div>
          </div>
        </div>

        <div className="filters-row">
          <div>
            <label>Categorías</label>
            <select multiple value={filters.categoria_ids} onChange={(e) => setFilters({ ...filters, categoria_ids: Array.from(e.target.selectedOptions).map((o) => Number(o.value)) })}>
              {categorias?.map((cat) => (
                <option key={cat.id} value={cat.id}>{cat.nombre}</option>
              ))}
            </select>
          </div>
          <div>
            <label>Tipo</label>
            <select multiple value={filters.tipo_ids} onChange={(e) => setFilters({ ...filters, tipo_ids: Array.from(e.target.selectedOptions).map((o) => Number(o.value)) })}>
              {TIPOS.map((tipo) => (
                <option key={tipo.id} value={tipo.id}>{tipo.nombre}</option>
              ))}
            </select>
          </div>
          <div>
            <label>Método de pago</label>
            <select multiple value={filters.metodo_pago_ids} onChange={(e) => setFilters({ ...filters, metodo_pago_ids: Array.from(e.target.selectedOptions).map((o) => Number(o.value)) })}>
              {metodos?.map((m) => (
                <option key={m.id} value={m.id}>{m.nombre}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="filters-row">
          <div>
            <label>Importe mínimo</label>
            <input type="number" value={filters.importe_min} onChange={(e) => setFilters({ ...filters, importe_min: e.target.value })} />
          </div>
          <div>
            <label>Importe máximo</label>
            <input type="number" value={filters.importe_max} onChange={(e) => setFilters({ ...filters, importe_max: e.target.value })} />
          </div>
          <div>
            <label>Búsqueda</label>
            <input type="search" placeholder="Concepto o notas" value={searchInput} onChange={(e) => setSearchInput(e.target.value)} />
          </div>
          <div className="toggle-group">
            <label>
              <input type="checkbox" checked={filters.solo_gastos_fijos} onChange={(e) => setFilters({ ...filters, solo_gastos_fijos: e.target.checked })} /> Solo gastos fijos
            </label>
            <label>
              <input type="checkbox" checked={filters.solo_gastos_variables} onChange={(e) => setFilters({ ...filters, solo_gastos_variables: e.target.checked })} /> Solo gastos variables
            </label>
          </div>
        </div>

        <div className="filters-actions">
          <div className="saved-views">
            <label>Vistas guardadas</label>
            <select onChange={(e) => {
              const vista = savedViews.find((v) => v.name === e.target.value)
              if (vista) applyView(vista)
            }}>
              <option value="">Seleccionar vista</option>
              {savedViews.map((v) => (
                <option key={v.name} value={v.name}>{v.name}</option>
              ))}
            </select>
            {savedViews.map((v) => (
              <button key={v.name} className="link" onClick={() => deleteView(v.name)}>Eliminar {v.name}</button>
            ))}
          </div>
          <div className="btn-row">
            <button className="btn" onClick={handleApplyFilters}>Aplicar filtros</button>
            <button className="btn secondary" onClick={handleClearFilters}>Limpiar</button>
          </div>
        </div>
      </section>

      <div className="content-grid">
        <div className="main-table">
          <MovimientosTable
            data={tableData}
            isLoading={isLoading}
            sorting={sorting}
            onSortChange={(value) => setSorting(value || { id: 'fecha', desc: true })}
            grouping={grouping}
            onGroupChange={setGrouping}
            onInlineUpdate={onInlineUpdate}
            categories={categorias}
            aggregates={data?.aggregates}
            onRowClick={(row) => setSelectedRow(row)}
            selectedRowId={selectedRow?.id}
          />
          <div className="pagination">
            <div>Mostrando página {page} de {totalPages} · {data?.total_items || 0} registros</div>
            <div className="btn-row">
              <button disabled={page === 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>Anterior</button>
              <button disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>Siguiente</button>
              <select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1) }}>
                {[25, 50, 100, 200].map((size) => (
                  <option key={size} value={size}>{size} por página</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <aside className="side-panel card">
          <h3>Panel de contexto</h3>
          {selectedRow ? (
            <div>
              <p><strong>Fecha:</strong> {selectedRow.fecha}</p>
              <p><strong>Concepto:</strong> {selectedRow.concepto}</p>
              <p><strong>Importe:</strong> {selectedRow.importe}</p>
              <p><strong>Tipo:</strong> {selectedRow.tipo_nombre}</p>
              <p><strong>Categoría:</strong> {selectedRow.categoria_nombre || '—'}</p>
              <p><strong>Método:</strong> {selectedRow.metodo_pago_nombre || '—'}</p>
              <p><strong>Notas:</strong> {selectedRow.notas || 'Sin notas'}</p>
              <div className="muted small">
                <p>Total en categoría (filtros actuales): {categoriaSummary?.aggregates?.total_importe?.toFixed(2)}</p>
                <p>Movimientos en categoría: {categoriaSummary?.aggregates?.total_registros}</p>
              </div>
            </div>
          ) : (
            <p>Selecciona una fila para ver detalles y contexto.</p>
          )}
        </aside>
      </div>
    </Layout>
  )
}
