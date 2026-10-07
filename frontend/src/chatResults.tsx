import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'
import type { ProductSummary } from './api'

// Holds the products the chat agent last returned, so the page can render them
// as product cards outside the chat panel (Problem 7 handoff).
type ChatResults = {
  query: string
  products: ProductSummary[]
}

type ChatResultsContextValue = {
  results: ChatResults | null
  showResults: (query: string, products: ProductSummary[]) => void
  clearResults: () => void
}

const ChatResultsContext = createContext<ChatResultsContextValue | null>(null)

export function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [results, setResults] = useState<ChatResults | null>(null)
  // Stable callbacks so effects that depend on them don't re-run every render.
  const showResults = useCallback((query: string, products: ProductSummary[]) => setResults({ query, products }), [])
  const clearResults = useCallback(() => setResults(null), [])
  const value = useMemo<ChatResultsContextValue>(
    () => ({ results, showResults, clearResults }),
    [results, showResults, clearResults],
  )
  return <ChatResultsContext.Provider value={value}>{children}</ChatResultsContext.Provider>
}

export function useChatResults() {
  const context = useContext(ChatResultsContext)
  if (!context) throw new Error('useChatResults must be used within ChatResultsProvider')
  return context
}
