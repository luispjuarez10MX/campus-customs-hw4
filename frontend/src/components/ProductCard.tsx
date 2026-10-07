import { Link } from 'react-router-dom'
import { formatPrice, type ProductSummary } from '../api'

export default function ProductCard({ product }: { product: ProductSummary }) {
  const soldOut = product.total_stock === 0
  const lowStock = !soldOut && product.total_stock <= 10

  return (
    <Link to={`/products/${product.product_id}`} className="product-card">
      <div className="product-card-media">
        <img src={product.image_url} alt={product.name} loading="lazy" />
        {soldOut && <span className="badge badge-muted">Sold out</span>}
        {lowStock && <span className="badge badge-gold">Low stock</span>}
        <span className="product-card-cta">View details →</span>
      </div>
      <div className="product-card-body">
        <span className="product-tag">{product.garment_type}</span>
        <h3>{product.name}</h3>
        <p className="muted">{product.short_description}</p>
        <p className="price">{formatPrice(product.price)}</p>
      </div>
    </Link>
  )
}
