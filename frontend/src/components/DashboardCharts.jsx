import React from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Cell
} from 'recharts'
import SimpleTable from './SimpleTable'

/**
 * Colección de componentes de gráficos para el dashboard.
 * Cada bloque está encapsulado para mantener el JSX de la página principal
 * conciso y favorecer la reutilización futura.
 */
export default function DashboardCharts({ monthly, byCategory, yearly, isLoading }) {
  const palette = ['#0ea5e9', '#6366f1', '#22c55e', '#f97316', '#a855f7', '#e11d48', '#0ea5e9aa']

  if (isLoading) {
    return <p className="muted">Cargando visualizaciones...</p>
  }

  if (!monthly?.length && !byCategory?.length && !yearly?.length) {
    return <p className="muted">No hay datos para mostrar en el dashboard.</p>
  }

  return (
    <div className="charts-grid">
      <div className="card chart-card">
        <h3>Evolución mensual</h3>
        {monthly?.length ? (
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={monthly} margin={{ left: 0, right: 0, top: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="mes_anio" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="balance_neto" stroke="#0ea5e9" name="Balance" strokeWidth={3} />
              <Line type="monotone" dataKey="total_gastos" stroke="#ef4444" name="Gastos" />
              <Line type="monotone" dataKey="total_ingresos" stroke="#22c55e" name="Ingresos" />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="muted">Sin datos mensuales en este rango.</p>
        )}
      </div>

      <div className="card chart-card">
        <h3>Distribución por categoría</h3>
        {byCategory?.length ? (
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Tooltip />
              <Legend />
              <Pie dataKey="total_gastos" data={byCategory} nameKey="categoria_nombre" label>
                {byCategory.map((entry, index) => (
                  <Cell key={entry.categoria_nombre} fill={palette[index % palette.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <p className="muted">No hay gastos en las categorías seleccionadas.</p>
        )}
      </div>

      <div className="card chart-card">
        <h3>Comparativa anual</h3>
        {yearly?.length ? (
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={yearly} margin={{ top: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="anio" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="total_ingresos" fill="#22c55e" name="Ingresos" stackId="totales" />
              <Bar dataKey="total_gastos" fill="#ef4444" name="Gastos" stackId="totales" />
              <Bar dataKey="balance_neto" fill="#0ea5e9" name="Balance" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="muted">No hay datos anuales.</p>
        )}
      </div>

      <div className="card chart-card">
        <h3>Top categorías</h3>
        {byCategory?.length ? (
          <SimpleTable
            columns={[
              { key: 'categoria_nombre', label: 'Categoría' },
              { key: 'total_gastos', label: 'Gastos' },
              { key: 'porcentaje_sobre_total', label: '% sobre total' }
            ]}
            data={byCategory.slice(0, 8).map((item) => ({
              ...item,
              total_gastos: `€ ${item.total_gastos.toFixed(2)}`,
              porcentaje_sobre_total: `${item.porcentaje_sobre_total.toFixed(1)}%`
            }))}
          />
        ) : (
          <p className="muted">Sin distribución de categorías.</p>
        )}
      </div>
    </div>
  )
}
