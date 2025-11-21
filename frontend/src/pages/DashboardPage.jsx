import { useQuery } from '@tanstack/react-query'
import Layout from '../components/Layout'
import Card from '../components/Card'
import SimpleTable from '../components/SimpleTable'
import { fetcher } from '../api/client'

export default function DashboardPage() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['dashboard'], queryFn: () => fetcher('/dashboard') })

  return (
    <Layout>
      <h1>Panel analítico</h1>
      <p style={{ color: '#64748b' }}>KPIs rápidos y distribuciones resumidas.</p>
      {isLoading && <p>Cargando panel...</p>}
      {isError && <p>No se pudo calcular el dashboard.</p>}
      {data && (
        <>
          <div className="card-grid">
            <Card title="Total ingresos" value={`€ ${data.kpis.total_ingresos.toFixed(2)}`} />
            <Card title="Total gastos" value={`€ ${data.kpis.total_gastos.toFixed(2)}`} />
            <Card title="Balance neto" value={`€ ${data.kpis.balance_neto.toFixed(2)}`} />
            <Card title="Media mensual" value={`€ ${data.kpis.media_mensual.toFixed(2)}`} />
            <Card title="Variación mensual" value={`€ ${data.kpis.variacion_mensual.toFixed(2)}`} />
            <Card
              title="Proyección 30d"
              value={`€ ${data.kpis.proyeccion_30d.toFixed(2)}`}
              hint={`60d: € ${data.kpis.proyeccion_60d.toFixed(2)}`}
            />
          </div>
          <h2>Saldo mensual</h2>
          <SimpleTable columns={[{ key: 'mes_anio', label: 'Mes' }, { key: 'saldo', label: 'Saldo' }]} data={data.serie_mensual} />

          <h2>Distribución por categoría</h2>
          <SimpleTable
            columns={[
              { key: 'categoria', label: 'Categoría' },
              { key: 'total', label: 'Total' }
            ]}
            data={data.distribucion_categoria}
          />
        </>
      )}
    </Layout>
  )
}
