import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { fetchProducts, type ProductSummary } from '../api'
import { CATEGORIES, categoryOf } from '../categories'
import ProductCard from '../components/ProductCard'
import ProductCardSkeleton from '../components/ProductCardSkeleton'

type SortKey = 'relevance' | 'price-asc' | 'price-desc' | 'name'

const SORTS: { id: SortKey; label: string }[] = [
  { id: 'relevance', label: 'Featured' },
  { id: 'price-asc', label: 'Price: low to high' },
  { id: 'price-desc', label: 'Price: high to low' },
  { id: 'name', label: 'Name: A–Z' },
]

export default function Products() {
  const [products, setProducts] = useState<ProductSummary[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchParams, setSearchParams] = useSearchParams()

  const category = searchParams.get('category') ?? ''
  const query = searchParams.get('q') ?? ''
  const sort = (searchParams.get('sort') as SortKey) || 'relevance'
  const inStockOnly = searchParams.get('stock') === '1'

  function load() {
    setLoading(true)
    setError(null)
    fetchProducts()
      .then(setProducts)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const visible = useMemo(() => {
    const words = query.toLowerCase().split(/\s+/).filter(Boolean)
    const filtered = products.filter((product) => {
      if (category && categoryOf(product.garment_type) !== category) return false
      if (inStockOnly && product.total_stock === 0) return false
      const text = `${product.name} ${product.garment_type} ${product.colors.join(' ')}`.toLowerCase()
      return words.every((word) => text.includes(word))
    })
    const sorted = [...filtered]
    if (sort === 'price-asc') sorted.sort((a, b) => a.price - b.price)
    else if (sort === 'price-desc') sorted.sort((a, b) => b.price - a.price)
    else if (sort === 'name') sorted.sort((a, b) => a.name.localeCompare(b.name))
    return sorted
  }, [products, category, query, sort, inStockOnly])

  function updateParam(key: string, value: string) {
    const next = new URLSearchParams(searchParams)
    if (value) next.set(key, value)
    else next.delete(key)
    setSearchParams(next, { replace: true })
  }

  function clearFilters() {
    setSearchParams(new URLSearchParams(), { replace: true })
  }

  const hasFilters = Boolean(query || category || inStockOnly)

  return (
    <>
      <h1>Products</h1>
      <div className="filters">
        <input
          type="search"
          value={query}
          onChange={(event) => updateParam('q', event.target.value)}
          placeholder="Search by name, type, or color"
          aria-label="Search products"
        />
        <div className="chips">
          <button type="button" className={category ? 'chip' : 'chip active'} onClick={() => updateParam('category', '')}>
            All
          </button>
          {CATEGORIES.map((item) => (
            <button
              key={item.id}
              type="button"
              className={category === item.id ? 'chip active' : 'chip'}
              onClick={() => updateParam('category', item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>
        <div className="filters-row">
          <label className="select-label">
            Sort
            <select value={sort} onChange={(event) => updateParam('sort', event.target.value)}>
              {SORTS.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={inStockOnly}
              onChange={(event) => updateParam('stock', event.target.checked ? '1' : '')}
            />
            In stock only
          </label>
          {hasFilters && (
            <button type="button" className="link-button" onClick={clearFilters}>
              Clear filters
            </button>
          )}
        </div>
      </div>

      {loading && (
        <div className="product-grid" aria-hidden>
          {Array.from({ length: 8 }).map((_, index) => (
            <ProductCardSkeleton key={index} />
          ))}
        </div>
      )}

      {error && (
        <div className="state-box error-box">
          <p>We couldn't load the products.</p>
          <p className="muted">{error}</p>
          <button type="button" className="button" onClick={load}>
            Try again
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          <p className="muted result-count">
            {visible.length} of {products.length} products
          </p>
          {visible.length === 0 ? (
            <div className="state-box">
              <p>No products match your search.</p>
              <p className="muted">Try fewer words or a different category.</p>
              {hasFilters && (
                <button type="button" className="button button-outline" onClick={clearFilters}>
                  Clear filters
                </button>
              )}
            </div>
          ) : (
            <div className="product-grid">
              {visible.map((product) => (
                <ProductCard key={product.product_id} product={product} />
              ))}
            </div>
          )}
        </>
      )}
    </>
  )
}
