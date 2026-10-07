import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

const linkClass = ({ isActive }: { isActive: boolean }) => (isActive ? 'nav-link active' : 'nav-link')

export default function NavBar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <header className="navbar">
      <Link to="/" className="brand">
        Campus Customs
      </Link>
      <nav className="nav-links">
        <NavLink to="/" end className={linkClass}>
          Home
        </NavLink>
        <NavLink to="/products" className={linkClass}>
          Products
        </NavLink>
        <NavLink to="/about" className={linkClass}>
          About Us
        </NavLink>
      </nav>
      <div className="nav-account">
        {user ? (
          <>
            <span className="nav-greeting">Hi, {user.first_name ?? user.email}</span>
            <button type="button" className="button button-small" onClick={handleLogout}>
              Log out
            </button>
          </>
        ) : (
          <>
            <NavLink to="/login" className={linkClass}>
              Log in
            </NavLink>
            <NavLink to="/create-account" className="button button-small">
              Create account
            </NavLink>
          </>
        )}
      </div>
    </header>
  )
}
