import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import type { User } from './api'

type AuthContextValue = {
  user: User | null
  setUser: (user: User | null) => void
  logout: () => void
}

const STORAGE_KEY = 'campus-customs-user'
const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUserState] = useState<User | null>(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved ? (JSON.parse(saved) as User) : null
  })

  useEffect(() => {
    if (user) localStorage.setItem(STORAGE_KEY, JSON.stringify(user))
    else localStorage.removeItem(STORAGE_KEY)
  }, [user])

  const value: AuthContextValue = {
    user,
    setUser: setUserState,
    logout: () => setUserState(null),
  }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
