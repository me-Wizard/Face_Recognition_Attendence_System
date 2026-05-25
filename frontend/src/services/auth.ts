// src/services/auth.ts

import axios from 'axios'
import Cookies from 'js-cookie'
import type { LoginResponse } from '@/types'

const BASE = process.env.NEXT_PUBLIC_API_URL

const TOKEN_KEY = 'fa_token'
const USER_KEY  = 'fa_user'

export const authService = {
  async login(email: string, password: string): Promise<LoginResponse> {
    const res = await axios.post<LoginResponse>(`${BASE}/auth/login`, { email, password })
    const data = res.data
    Cookies.set(TOKEN_KEY, data.access_token, { expires: 1 })
    localStorage.setItem(USER_KEY, JSON.stringify({
      name:        data.name,
      email:       data.email,
      role:        data.role,
      employee_id: data.employee_id,
    }))
    return data
  },

  logout() {
    Cookies.remove(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },

  getToken(): string | undefined {
    return Cookies.get(TOKEN_KEY)
  },

  getUser() {
    if (typeof window === 'undefined') return null
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  },

  isLoggedIn(): boolean {
    return !!Cookies.get(TOKEN_KEY)
  },
}
