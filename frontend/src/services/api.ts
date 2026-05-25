// src/services/api.ts

import axios from 'axios'
import { authService } from './auth'
import type {
  AttendanceToday, AttendanceHistory,
  AbsentUsers, SystemStatus, AttendanceStatus, AdminAccount,
} from '@/types'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10000,
})

api.interceptors.request.use(config => {
  const token = authService.getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      authService.logout()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const attendanceApi = {
  getToday: () =>
    api.get<AttendanceToday>('/attendance/today').then(r => r.data),

  getHistory: (params?: {
    employee_id?: string
    from_date?:   string
    to_date?:     string
    page?:        number
    page_size?:   number
  }) => api.get<AttendanceHistory>('/attendance/history', { params }).then(r => r.data),

  getAbsent: () =>
    api.get<AbsentUsers>('/attendance/absent').then(r => r.data),

  getStatus: () =>
    api.get<AttendanceStatus>('/attendance/status').then(r => r.data),

  exportCsv: () =>
    api.get('/attendance/export/csv', { responseType: 'blob' }).then(r => r.data),
}

export const systemApi = {
  getStatus: () =>
    api.get<SystemStatus>('/system/status').then(r => r.data),
}

export const enrollApi = {
  getUser: (employee_id: string) =>
    api.get(`/enroll/${employee_id}`).then(r => r.data),

  deleteUser: (employee_id: string) =>
    api.delete(`/enroll/${employee_id}`).then(r => r.data),

  startEnrollment: (data: { name: string; employee_id: string; department: string }) =>
    api.post('/enroll/start', data).then(r => r.data),
}

export const recognitionApi = {
  startLoop: () => api.get('/recognize/start').then(r => r.data),
  recognize: () => api.post('/recognize').then(r => r.data),
}

export const authApi = {
  me: () => api.get('/auth/me').then(r => r.data),

  register: (data: {
    name: string; email: string; password: string
    role: string; employee_id?: string
  }) => api.post('/auth/register', data).then(r => r.data),

  listUsers: () => api.get<AdminAccount[]>('/auth/users').then(r => r.data),
}
