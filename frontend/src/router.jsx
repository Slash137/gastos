import { createBrowserRouter } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import MovimientosPage from './pages/MovimientosPage'
import CategoriasPage from './pages/CategoriasPage'
import ReglasPage from './pages/ReglasPage'
import ImportPage from './pages/ImportPage'

const router = createBrowserRouter([
  { path: '/', element: <DashboardPage /> },
  { path: '/movimientos', element: <MovimientosPage /> },
  { path: '/categorias', element: <CategoriasPage /> },
  { path: '/reglas', element: <ReglasPage /> },
  { path: '/importar', element: <ImportPage /> }
])

export default router
