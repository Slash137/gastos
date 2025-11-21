import { useQuery } from '@tanstack/react-query'
import Layout from '../components/Layout'
import SimpleTable from '../components/SimpleTable'
import { fetcher } from '../api/client'

export default function ReglasPage() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['reglas'], queryFn: () => fetcher('/reglas') })

  return (
    <Layout>
      <h1>Reglas automáticas</h1>
      <p style={{ color: '#64748b' }}>
        Define patrones de texto para autocategorizar movimientos según el concepto o las notas.
      </p>
      {isLoading && <p>Cargando reglas...</p>}
      {isError && <p>No se pudieron cargar las reglas.</p>}
      {data && (
        <SimpleTable
          columns={[
            { key: 'pattern', label: 'Patrón' },
            { key: 'campo_objetivo', label: 'Campo' },
            { key: 'categoria_id', label: 'Categoría' }
          ]}
          data={data}
        />
      )}
    </Layout>
  )
}
