// Types and fetch helpers for the FastAPI backend (mirrors backend/models.py)

export type SizeStock = {
  size: string
  quantity: number
}

export type ProductSummary = {
  product_id: string
  name: string
  garment_type: string
  price: number
  short_description: string
  colors: string[]
  image_url: string
  total_stock: number
}

export type ProductDetail = ProductSummary & {
  description: string
  search_tags: string[]
  inventory: SizeStock[]
}

async function getJson<T>(url: string): Promise<T> {
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(response.status === 404 ? 'Not found' : `Request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

export const fetchProducts = () => getJson<ProductSummary[]>('/api/products')

export const fetchProduct = (productId: string) =>
  getJson<ProductDetail>(`/api/products/${encodeURIComponent(productId)}`)

export const formatPrice = (price: number) => `$${price.toFixed(2)}`

// ---- Accounts (Problem 4) ----

export type User = {
  id: number
  first_name: string | null
  last_name: string | null
  email: string
}

export type SignupBody = {
  first_name: string
  last_name: string
  email: string
  password: string
}

async function postJson<T>(url: string, body: unknown): Promise<T> {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error((data as { detail?: string }).detail ?? `Request failed (${response.status})`)
  }
  return data as T
}

export const signup = (body: SignupBody) => postJson<User>('/api/auth/signup', body)

export const login = (email: string, password: string) =>
  postJson<User>('/api/auth/login', { email, password })

// ---- Chat (Problems 5 & 7) ----

export type ChatTurn = {
  role: 'user' | 'assistant'
  content: string
}

// The chat returns products in the SAME shape as /api/products, so the frontend
// renders them with the same ProductCard component as the Products page (Problem 7).
export type ChatResponse = {
  reply: string
  products: ProductSummary[]
}

export const sendChat = (messages: ChatTurn[], userId: number | null, currentProductId: string | null) =>
  postJson<ChatResponse>('/api/chat', {
    messages,
    user_id: userId,
    current_product_id: currentProductId,
  })

// ---- Chat history (Problem 8) ----

export type ChatHistoryMessage = {
  role: 'user' | 'assistant'
  content: string
  products: ProductSummary[]
}

export const fetchChatHistory = (userId: number) =>
  getJson<{ messages: ChatHistoryMessage[] }>(`/api/chat/history?user_id=${userId}`)
