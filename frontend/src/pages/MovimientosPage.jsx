import Layout from '../components/Layout'
import SimpleTable from '../components/SimpleTable'
import { useMovimientos } from '../hooks/useMovimientos'

export default function MovimientosPage() {
  const { data, isLoading, isError } = useMovimientos()

  return (
    <Layout>
      <h1>Movimientos</h1>
      <p style={{ color: '#64748b' }}>Lista de gastos e ingresos con filtros básicos.</p>
      {isLoading && <p>Cargando movimientos...</p>}
      {isError && <p>Ha ocurrido un error al cargar los datos.</p>}
      {data && (
        <SimpleTable
          columns={[
            { key: 'fecha', label: 'Fecha' },
            { key: 'concepto', label: 'Concepto' },
            { key: 'importe', label: 'Importe' },
            { key: 'categoria_id', label: 'Categoría' },
            { key: 'metodo_pago_id', label: 'Método pago' }
          ]}
          data={data}
        />
      )}
    </Layout>
  )
}
