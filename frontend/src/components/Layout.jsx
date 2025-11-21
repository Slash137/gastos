import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/movimientos', label: 'Movimientos' },
  { to: '/categorias', label: 'Categorías' },
  { to: '/reglas', label: 'Reglas' },
  { to: '/importar', label: 'Importar' }
]

export default function Layout({ children }) {
  return (
    <div className="layout">
      <header className="navbar">
        <div>
          <strong>Gastos</strong>
          <span className="badge" style={{ marginLeft: 8 }}>Beta</span>
        </div>
        <nav className="nav-links">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="container">{children}</main>
    </div>
  )
}
