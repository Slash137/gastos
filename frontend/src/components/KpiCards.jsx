import React from 'react'
import Card from './Card'

/**
 * Grupo de KPIs principales del dashboard.
 * Se separa en un componente reutilizable para mantener el JSX del page limpio
 * y favorecer el reuso en futuras vistas.
 */
export default function KpiCards({ summary, isLoading }) {
  const formatCurrency = (value) => `€ ${Number(value || 0).toFixed(2)}`

  if (isLoading) {
    return <p className="muted">Calculando KPIs...</p>
  }

  if (!summary) {
    return <p className="muted">No hay datos para los filtros seleccionados.</p>
  }

  const variacionPositiva = summary.variacion_mensual_porcentaje !== null && summary.variacion_mensual_porcentaje >= 0

  return (
    <div className="card-grid">
      <Card title="Total gastos" value={formatCurrency(summary.total_gastos)} />
      <Card title="Total ingresos" value={formatCurrency(summary.total_ingresos)} />
      <Card title="Balance neto" value={formatCurrency(summary.balance_neto)} />
      <Card title="Gasto medio mensual" value={formatCurrency(summary.gasto_medio_mensual)} />
      <Card
        title="Variación vs mes anterior"
        value={
          summary.variacion_mensual_porcentaje !== null
            ? `${summary.variacion_mensual_porcentaje.toFixed(1)}%`
            : 'N/D'
        }
        hint="Comparación de gasto mensual"
      />
      <Card
        title="Proyección 30d"
        value={summary.proyeccion_saldo_30d !== null ? formatCurrency(summary.proyeccion_saldo_30d) : 'N/D'}
        hint={
          summary.proyeccion_saldo_60d !== null
            ? `60d: ${formatCurrency(summary.proyeccion_saldo_60d)}`
            : 'Sin suficiente histórico'
        }
      />
      <Card
        title="Tendencia"
        value={summary.variacion_mensual_porcentaje !== null ? (variacionPositiva ? 'Positiva' : 'Negativa') : 'N/D'}
        hint={
          summary.variacion_mensual_porcentaje !== null
            ? `${summary.variacion_mensual_porcentaje.toFixed(1)}% respecto al mes anterior`
            : 'Sin datos de dos meses consecutivos'
        }
      />
    </div>
  )
}
