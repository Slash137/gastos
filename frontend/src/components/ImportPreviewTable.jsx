import PropTypes from 'prop-types'

/**
 * Tabla ligera para mostrar la previsualización del CSV.
 * Resalta duplicados y filas con errores.
 */
export default function ImportPreviewTable({ rows }) {
  if (!rows?.length) return <p>No hay filas para mostrar.</p>

  return (
    <div className="card" style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>Idx</th>
            <th>Fecha</th>
            <th>Concepto</th>
            <th>Importe</th>
            <th>Saldo</th>
            <th>Tipo</th>
            <th>Categoría</th>
            <th>Método</th>
            <th>Notas</th>
            <th>Duplicado</th>
            <th>Errores</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr
              key={row.raw_index}
              style={{
                background: row.errors.length ? '#fee2e2' : row.is_duplicate ? '#fef9c3' : 'transparent'
              }}
            >
              <td>{row.raw_index}</td>
              <td>{row.fecha || '-'}</td>
              <td>{row.concepto}</td>
              <td>{row.importe ?? '-'}</td>
              <td>{row.saldo ?? '-'}</td>
              <td>{row.tipo_id ?? '-'}</td>
              <td>{row.categoria_id ?? '-'}</td>
              <td>{row.metodo_pago_id ?? '-'}</td>
              <td>{row.notas || '-'}</td>
              <td>{row.is_duplicate ? 'Sí' : 'No'}</td>
              <td>{row.errors.join(', ') || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

ImportPreviewTable.propTypes = {
  rows: PropTypes.arrayOf(PropTypes.object)
}

