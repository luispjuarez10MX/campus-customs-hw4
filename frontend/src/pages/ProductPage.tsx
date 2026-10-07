import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchProduct, formatPrice, type ProductDetail } from '../api'

export default function ProductPage() {
  const { productId = '' } = useParams()
  // Result tagged with the id it belongs to, so navigating to another product shows "Loading…"
  const [result, setResult] = useState<{ id: string; product?: ProductDetail; error?: string }>()

  useEffect(() => {
    fetchProduct(productId)
      .then((product) => setResult({ id: productId, product }))
      .catch((err: Error) => setResult({ id: productId, error: err.message }))
  }, [productId])

  const current = result?.id === productId ? result : undefined
  const product = current?.product
  const error = current?.error

  if (error) {
    const notFound = error === 'Not found'
    return (
      <div className="state-box error-box">
        <p>{notFound ? 'We couldn’t find that product.' : 'Something went wrong loading this product.'}</p>
        {!notFound && <p className="muted">{error}</p>}
        <Link to="/products" className="button">
          ← Back to products
        </Link>
      </div>
    )
  }
  if (!product) {
    return (
      <div className="product-detail" aria-hidden>
        <div className="skeleton-img detail" />
        <div>
          <div className="skeleton-line" style={{ width: '40%' }} />
          <div className="skeleton-line" style={{ width: '70%', height: '1.6rem' }} />
          <div className="skeleton-line" style={{ width: '25%' }} />
          <div className="skeleton-line" style={{ width: '100%' }} />
          <div className="skeleton-line" style={{ width: '90%' }} />
        </div>
      </div>
    )
  }

  return (
    <>
      <Link to="/products" className="back-link">
        ← Back to products
      </Link>
      <div className="product-detail">
        <img src={product.image_url} alt={product.name} />
        <div>
          <p className="eyebrow">{product.garment_type}</p>
          <h1>{product.name}</h1>
          <p className="price price-large">{formatPrice(product.price)}</p>
          <p>{product.description}</p>
          <p className="muted">Colors: {product.colors.join(', ')}</p>

          <h2 className="stock-title">Sizes & stock</h2>
          {product.inventory.length === 0 ? (
            <p className="muted">Stock information is not available for this product.</p>
          ) : (
            <div className="size-grid">
              {product.inventory.map((item) => (
                <div key={item.size} className={item.quantity > 0 ? 'size-box' : 'size-box sold-out'}>
                  <strong>{item.size}</strong>
                  <span>{item.quantity > 0 ? `${item.quantity} left` : 'Out of stock'}</span>
                </div>
              ))}
            </div>
          )}
          <p className="muted">{product.total_stock} units in stock across all sizes.</p>
        </div>
      </div>
    </>
  )
}
