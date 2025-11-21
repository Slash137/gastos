import { useQuery } from '@tanstack/react-query'
import Layout from '../components/Layout'
import SimpleTable from '../components/SimpleTable'
import { fetcher } from '../api/client'

export default function CategoriasPage() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['categorias'], queryFn: () => fetcher('/categorias') })

  return (
    <Layout>
      <h1>Categorías</h1>
      <p style={{ color: '#64748b' }}>Administra las categorías y marca cuáles son gastos fijos.</p>
      {isLoading && <p>Cargando categorías...</p>}
      {isError && <p>No se pudieron cargar las categorías.</p>}
      {data && (
        <SimpleTable columns={[{ key: 'nombre', label: 'Nombre' }, { key: 'es_fijo', label: 'Fijo' }]} data={data} />
      )}
    </Layout>
  )
}
