// Placeholder shown while products load, so the grid doesn't jump when data arrives.
export default function ProductCardSkeleton() {
  return (
    <div className="product-card skeleton">
      <div className="skeleton-img" />
      <div className="product-card-body">
        <div className="skeleton-line" style={{ width: '80%' }} />
        <div className="skeleton-line" style={{ width: '30%' }} />
        <div className="skeleton-line" style={{ width: '95%' }} />
      </div>
    </div>
  )
}
