import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Layout from '../components/Layout'
import DashboardFilters from '../components/DashboardFilters'
import KpiCards from '../components/KpiCards'
import DashboardCharts from '../components/DashboardCharts'
import { fetcher } from '../api/client'

const TIPOS = [
  { id: 1, nombre: 'Gasto' },
  { id: 2, nombre: 'Ingreso' }
]

const defaultFilters = {
  fecha_desde: '',
  fecha_hasta: '',
  categoria_ids: [],
  tipo_ids: [],
  metodo_pago_ids: [],
  solo_gastos_fijos: false,
  solo_gastos_variables: false
}

const formatDate = (date) => date.toISOString().slice(0, 10)

const serializeFilters = (params = {}) => {
  const searchParams = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return
    if (Array.isArray(value)) {
      if (value.length) searchParams.set(key, value.join(','))
    } else {
      searchParams.set(key, value)
    }
  })
  const query = searchParams.toString()
  return { query, searchParams }
}

export default function DashboardPage() {
  const [filters, setFilters] = useState({ ...defaultFilters })
  const [appliedFilters, setAppliedFilters] = useState({ ...defaultFilters })

  const { query } = useMemo(() => serializeFilters(appliedFilters), [appliedFilters])
  const querySuffix = query ? `?${query}` : ''

  const { data: categorias } = useQuery({ queryKey: ['categorias'], queryFn: () => fetcher('/categorias') })
  const { data: metodos } = useQuery({ queryKey: ['metodos_pago'], queryFn: () => fetcher('/metodos-pago') })

  const summaryQuery = useQuery({
    queryKey: ['dashboard', 'summary', query],
    queryFn: () => fetcher(`/dashboard/summary${querySuffix}`),
    keepPreviousData: true
  })

  const monthlyQuery = useQuery({
    queryKey: ['dashboard', 'monthly', query],
    queryFn: () => fetcher(`/dashboard/monthly${querySuffix}`),
    keepPreviousData: true
  })

  const categoryQuery = useQuery({
    queryKey: ['dashboard', 'by-category', query],
    queryFn: () => fetcher(`/dashboard/by-category${querySuffix}`),
    keepPreviousData: true
  })

  const yearlyQuery = useQuery({
    queryKey: ['dashboard', 'yearly', query],
    queryFn: () => fetcher(`/dashboard/yearly${querySuffix}`),
    keepPreviousData: true
  })

  const handleDatePreset = (preset) => {
    const now = new Date()
    let desde = ''
    let hasta = formatDate(now)
    switch (preset) {
      case 'hoy':
        desde = formatDate(now)
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
  }

  const handleApplyFilters = () => setAppliedFilters({ ...filters })
  const handleClearFilters = () => {
    setFilters({ ...defaultFilters })
    setAppliedFilters({ ...defaultFilters })
  }

  const loadingCharts = monthlyQuery.isLoading || categoryQuery.isLoading || yearlyQuery.isLoading

  return (
    <Layout>
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p className="muted">Resumen visual de tus finanzas domésticas.</p>
        </div>
      </div>

      <DashboardFilters
        filters={filters}
        setFilters={setFilters}
        onApply={handleApplyFilters}
        onClear={handleClearFilters}
        categorias={categorias || []}
        metodos={metodos || []}
        tipos={TIPOS}
        onPreset={handleDatePreset}
      />

      <section style={{ marginTop: 16 }}>
        <KpiCards summary={summaryQuery.data} isLoading={summaryQuery.isLoading} />
      </section>

      <section style={{ marginTop: 16 }}>
        <DashboardCharts
          monthly={monthlyQuery.data}
          byCategory={categoryQuery.data}
          yearly={yearlyQuery.data}
          isLoading={loadingCharts}
        />
      </section>
    </Layout>
  )
}
