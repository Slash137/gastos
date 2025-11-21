import React from 'react'

/**
 * Barra de filtros reutilizable para el dashboard.
 * Sigue el mismo lenguaje visual que la página de movimientos pero limita
 * los campos a los necesarios para las vistas agregadas.
 */
export default function DashboardFilters({
  filters,
  setFilters,
  onApply,
  onClear,
  categorias = [],
  metodos = [],
  tipos = [],
  onPreset
}) {
  const handleArrayChange = (key, values) => {
    const parsed = Array.from(values)?.map((v) => Number(v))
    setFilters((prev) => ({ ...prev, [key]: parsed }))
  }

  const toggleFlag = (key) => {
    setFilters((prev) => {
      const updated = { ...prev, [key]: !prev[key] }
      // Evitamos que fijos y variables estén activos simultáneamente.
      if (key === 'solo_gastos_fijos' && !prev[key]) {
        updated.solo_gastos_variables = false
      }
      if (key === 'solo_gastos_variables' && !prev[key]) {
        updated.solo_gastos_fijos = false
      }
      return updated
    })
  }

  return (
    <section className="filters card">
      <div className="filters-row">
        <div>
          <label>Desde</label>
          <input
            type="date"
            value={filters.fecha_desde}
            onChange={(e) => setFilters((prev) => ({ ...prev, fecha_desde: e.target.value }))}
          />
        </div>
        <div>
          <label>Hasta</label>
          <input
            type="date"
            value={filters.fecha_hasta}
            onChange={(e) => setFilters((prev) => ({ ...prev, fecha_hasta: e.target.value }))}
          />
        </div>
        <div>
          <label>Tipo</label>
          <select
            value={filters.tipo_ids[0] || ''}
            onChange={(e) => setFilters((prev) => ({ ...prev, tipo_ids: e.target.value ? [Number(e.target.value)] : [] }))}
          >
            <option value="">Ambos</option>
            {tipos.map((tipo) => (
              <option key={tipo.id} value={tipo.id}>
                {tipo.nombre}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label>Categorías</label>
          <select multiple value={filters.categoria_ids} onChange={(e) => handleArrayChange('categoria_ids', e.target.selectedOptions)}>
            {categorias.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.nombre}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label>Métodos de pago</label>
          <select multiple value={filters.metodo_pago_ids} onChange={(e) => handleArrayChange('metodo_pago_ids', e.target.selectedOptions)}>
            {metodos.map((met) => (
              <option key={met.id} value={met.id}>
                {met.nombre}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="filters-row">
        <div className="preset-buttons">
          <span>Rangos rápidos</span>
          <div className="chips">
            <button type="button" onClick={() => onPreset('hoy')}>
              Hoy
            </button>
            <button type="button" onClick={() => onPreset('mes')}>
              Este mes
            </button>
            <button type="button" onClick={() => onPreset('anio')}>
              Año actual
            </button>
            <button type="button" onClick={() => onPreset('12m')}>
              Últimos 12 meses
            </button>
          </div>
        </div>
        <div className="chips" style={{ alignItems: 'center' }}>
          <label className="small">
            <input type="checkbox" checked={filters.solo_gastos_fijos} onChange={() => toggleFlag('solo_gastos_fijos')} /> Solo gastos
            fijos
          </label>
          <label className="small">
            <input
              type="checkbox"
              checked={filters.solo_gastos_variables}
              onChange={() => toggleFlag('solo_gastos_variables')}
            />
            Solo gastos variables
          </label>
        </div>
      </div>

      <div className="filters-actions">
        <div className="btn-row">
          <button className="btn" type="button" onClick={onApply}>
            Aplicar filtros
          </button>
          <button className="btn secondary" type="button" onClick={onClear}>
            Limpiar
          </button>
        </div>
      </div>
    </section>
  )
}
