import { Route, Routes } from 'react-router-dom'
import ChatResultsBand from './components/ChatResultsBand'
import ChatWidget from './components/ChatWidget'
import NavBar from './components/NavBar'
import About from './pages/About'
import CreateAccount from './pages/CreateAccount'
import Home from './pages/Home'
import Login from './pages/Login'
import NotFound from './pages/NotFound'
import ProductPage from './pages/ProductPage'
import Products from './pages/Products'

export default function App() {
  return (
    <>
      <NavBar />
      <main className="page">
        <ChatResultsBand />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:productId" element={<ProductPage />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />
          <Route path="/create-account" element={<CreateAccount />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <footer className="footer">
        <p>© 2026 Campus Customs · Yale apparel for students, alumni, families, and fans</p>
      </footer>
      <ChatWidget />
    </>
  )
}
