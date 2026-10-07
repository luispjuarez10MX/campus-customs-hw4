import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchProducts, type ProductSummary } from '../api'
import { CATEGORIES, categoryOf } from '../categories'
import ProductCard from '../components/ProductCard'

export default function Home() {
  const [products, setProducts] = useState<ProductSummary[]>([])

  useEffect(() => {
    fetchProducts().then(setProducts).catch(() => setProducts([]))
  }, [])

  // One in-stock pick from each category
  const featured = CATEGORIES.map((category) =>
    products.find((product) => categoryOf(product.garment_type) === category.id && product.total_stock > 0),
  ).filter((product): product is ProductSummary => product !== undefined)

  return (
    <>
      <section className="hero">
        <p className="eyebrow">Yale apparel · New Haven</p>
        <h1>Wear your Bulldog pride every day.</h1>
        <p>
          Campus Customs makes comfortable, classic Yale gear for students, alumni, families, and fans. From game-day
          tees to residential college crewnecks, find the piece that feels like home.
        </p>
        <div className="hero-actions">
          <Link to="/products" className="button">
            Shop all products
          </Link>
          <Link to="/about" className="button button-outline">
            Our story
          </Link>
        </div>
      </section>

      <section className="section">
        <h2>Shop by category</h2>
        <div className="category-grid">
          {CATEGORIES.map((category) => (
            <Link key={category.id} to={`/products?category=${category.id}`} className="category-tile">
              {category.label}
            </Link>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="section-header">
          <h2>Featured picks</h2>
          <Link to="/products">View all →</Link>
        </div>
        <div className="product-grid">
          {featured.map((product) => (
            <ProductCard key={product.product_id} product={product} />
          ))}
        </div>
      </section>

      <section className="section value-row">
        <div>
          <h3>Made for the whole Yale family</h3>
          <p className="muted">Gear for students, grads, parents, and lifelong fans.</p>
        </div>
        <div>
          <h3>Colleges, teams, and traditions</h3>
          <p className="muted">Residential colleges, varsity sports, and The Game.</p>
        </div>
        <div>
          <h3>Questions? Just ask</h3>
          <p className="muted">Our chat assistant can help with sizes, stock, and prices.</p>
        </div>
      </section>
    </>
  )
}
