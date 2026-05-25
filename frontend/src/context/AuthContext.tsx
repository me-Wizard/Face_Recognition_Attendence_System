'use client'
// src/context/AuthContext.tsx

import {
  createContext, useContext, useState,
  useEffect, useCallback, type ReactNode,
} from 'react'
import { useRouter } from 'next/navigation'
import { authService } from '@/services/auth'
import type { AuthUser, Role } from '@/types'

interface AuthCtx {
  user:    AuthUser | null
  loading: boolean
  login:   (email: string, password: string) => Promise<void>
  logout:  () => void
  isAdmin: boolean
}

const Ctx = createContext<AuthCtx | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user,    setUser]    = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)
  const router                = useRouter()

  useEffect(() => {
    const stored = authService.getUser()
    if (stored && authService.isLoggedIn()) {
      setUser(stored)
    }
    setLoading(false)
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const data = await authService.login(email, password)
    const u: AuthUser = {
      name:        data.name,
      email:       data.email,
      role:        data.role,
      employee_id: data.employee_id,
    }
    setUser(u)
    router.push(data.role === 'admin' ? '/admin/dashboard' : '/user/dashboard')
  }, [router])

  const logout = useCallback(() => {
    authService.logout()
    setUser(null)
    router.push('/login')
  }, [router])

  return (
    <Ctx.Provider value={{ user, loading, login, logout, isAdmin: user?.role === 'admin' }}>
      {children}
    </Ctx.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useAuth must be inside AuthProvider')
  return ctx
}
