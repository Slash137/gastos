import PropTypes from 'prop-types'

/**
 * Selector de mapeo de columnas reutilizable para la importación.
 * Mantiene el estilo simple del resto de tablas pero permite cambiar
 * rápidamente cada rol (fecha, concepto, importe o debe/haber, etc.).
 */
export default function ImportMappingForm({ columns, mapping, setMapping }) {
  const opciones = columns.map((col) => ({ label: col, value: col }))
  const useDebeHaber = Boolean(mapping.debe_col || mapping.haber_col)

  const update = (field, value) => setMapping((prev) => ({ ...prev, [field]: value || null }))

  return (
    <div className="card" style={{ display: 'grid', gap: 12 }}>
      <div>
        <p style={{ margin: 0, fontWeight: 600 }}>Asignar columnas</p>
        <p style={{ margin: 0, color: '#64748b' }}>
          Usa los nombres detectados para que el sistema pueda normalizar los datos.
        </p>
      </div>
      <label className="field">
        <span>Fecha</span>
        <select value={mapping.fecha_col || ''} onChange={(e) => update('fecha_col', e.target.value)}>
          {opciones.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </label>
      <label className="field">
        <span>Concepto</span>
        <select value={mapping.concepto_col || ''} onChange={(e) => update('concepto_col', e.target.value)}>
          {opciones.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </label>

      <div className="field" style={{ gap: 8 }}>
        <span>Importe</span>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <input
              type="radio"
              checked={!useDebeHaber}
              onChange={() => update('debe_col', null) || update('haber_col', null)}
            />
            <span>Columna única</span>
          </label>
          <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <input type="radio" checked={useDebeHaber} onChange={() => update('importe_col', null)} />
            <span>Debe / Haber</span>
          </label>
        </div>
        {!useDebeHaber && (
          <select value={mapping.importe_col || ''} onChange={(e) => update('importe_col', e.target.value)}>
            {opciones.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        )}
        {useDebeHaber && (
          <div style={{ display: 'grid', gap: 8 }}>
            <select value={mapping.debe_col || ''} onChange={(e) => update('debe_col', e.target.value)}>
              {opciones.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <select value={mapping.haber_col || ''} onChange={(e) => update('haber_col', e.target.value)}>
              {opciones.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <label className="field">
        <span>Saldo (opcional)</span>
        <select value={mapping.saldo_col || ''} onChange={(e) => update('saldo_col', e.target.value)}>
          <option value="">-- Ninguno --</option>
          {opciones.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Notas (opcional)</span>
        <select value={mapping.notas_col || ''} onChange={(e) => update('notas_col', e.target.value)}>
          <option value="">-- Ninguno --</option>
          {opciones.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </label>
    </div>
  )
}

ImportMappingForm.propTypes = {
  columns: PropTypes.arrayOf(PropTypes.string).isRequired,
  mapping: PropTypes.object.isRequired,
  setMapping: PropTypes.func.isRequired
}

