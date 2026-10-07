import { useEffect, useRef, useState, type FormEvent } from 'react'
import { useLocation } from 'react-router-dom'
import { fetchChatHistory, sendChat, type ChatTurn } from '../api'
import { useAuth } from '../auth'
import { useChatResults } from '../chatResults'

type ChatMessage = ChatTurn & { shownCount?: number }

const WELCOME: ChatMessage = {
  role: 'assistant',
  content: "Hi! I'm the Campus Customs assistant. Ask me about our Yale gear, prices, sizes, or stock.",
}

// The product_id of the product page the customer is on, else null (page context).
function currentProductId(pathname: string): string | null {
  const match = pathname.match(/^\/products\/(.+)$/)
  return match ? decodeURIComponent(match[1]) : null
}

export default function ChatWidget() {
  const { user } = useAuth()
  const { showResults } = useChatResults()
  const location = useLocation()
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME])
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const listRef = useRef<HTMLDivElement>(null)

  // Reload saved history for a logged-in customer; reset to a fresh chat on logout.
  useEffect(() => {
    if (!user) {
      setMessages([WELCOME])
      return
    }
    let active = true
    fetchChatHistory(user.id)
      .then((history) => {
        if (!active) return
        if (history.messages.length === 0) {
          setMessages([WELCOME])
          return
        }
        setMessages(history.messages.map((m) => ({ role: m.role, content: m.content })))
        // Restore the product cards from the most recent assistant message that had any.
        const lastWithProducts = [...history.messages].reverse().find((m) => m.products.length > 0)
        if (lastWithProducts) showResults('your last search', lastWithProducts.products)
      })
      .catch(() => active && setMessages([WELCOME]))
    return () => {
      active = false
    }
  }, [user, showResults])

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight })
  }, [messages, open, sending])

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const text = draft.trim()
    if (!text || sending) return
    const history: ChatMessage[] = [...messages, { role: 'user', content: text }]
    setMessages(history)
    setDraft('')
    setSending(true)
    try {
      const turns: ChatTurn[] = history.map(({ role, content }) => ({ role, content }))
      const response = await sendChat(turns, user?.id ?? null, currentProductId(location.pathname))
      if (response.products.length > 0) showResults(text, response.products)
      setMessages((current) => [
        ...current,
        { role: 'assistant', content: response.reply, shownCount: response.products.length },
      ])
    } catch (err) {
      setMessages((current) => [...current, { role: 'assistant', content: `Sorry — ${(err as Error).message}` }])
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="chat-widget">
      {open && (
        <section className="chat-panel" aria-label="Campus Customs assistant">
          <header className="chat-header">
            <span>Campus Customs Assistant</span>
            <button type="button" className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat">
              ×
            </button>
          </header>
          <div className="chat-messages" ref={listRef}>
            {messages.map((message, index) => (
              <div key={index} className="chat-row">
                <div className={`chat-bubble ${message.role}`}>{message.content}</div>
                {message.shownCount ? (
                  <div className="chat-note">
                    Showing {message.shownCount} {message.shownCount === 1 ? 'product' : 'products'} on the page ↑
                  </div>
                ) : null}
              </div>
            ))}
            {sending && <div className="chat-bubble assistant typing">…</div>}
          </div>
          <form className="chat-input" onSubmit={handleSubmit}>
            <input
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Ask about merch, sizes, stock…"
              aria-label="Message"
            />
            <button type="submit" className="button" disabled={!draft.trim() || sending}>
              Send
            </button>
          </form>
        </section>
      )}
      <button
        type="button"
        className="chat-toggle"
        onClick={() => setOpen((value) => !value)}
        aria-label={open ? 'Close chat' : 'Open chat'}
      >
        {open ? '×' : 'Chat'}
      </button>
    </div>
  )
}
