import { useChatResults } from '../chatResults'
import ProductCard from './ProductCard'

// Renders the chat agent's latest product matches on the page, using the SAME
// ProductCard component as the Products page (Problem 3). Clicking a card opens
// the same single-product detail page. Shown on top of whatever page is active.
export default function ChatResultsBand() {
  const { results, clearResults } = useChatResults()
  if (!results || results.products.length === 0) return null

  return (
    <section className="chat-results" aria-label="Products from chat">
      <div className="chat-results-header">
        <h2>
          From the chat: <span className="muted">“{results.query}”</span>
        </h2>
        <button type="button" className="chip" onClick={clearResults}>
          Clear
        </button>
      </div>
      <div className="product-grid">
        {results.products.map((product) => (
          <ProductCard key={product.product_id} product={product} />
        ))}
      </div>
    </section>
  )
}
