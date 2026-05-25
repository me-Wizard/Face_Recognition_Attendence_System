// src/hooks/index.ts

import { useEffect, useRef, useState, useCallback } from 'react'
import { systemApi, attendanceApi } from '@/services/api'
import type { SystemStatus, AttendanceToday, AbsentUsers } from '@/types'

export function usePolling(cb: () => void, interval: number, enabled = true) {
  const ref = useRef(cb)
  ref.current = cb
  useEffect(() => {
    if (!enabled) return
    const id = setInterval(() => ref.current(), interval)
    return () => clearInterval(id)
  }, [interval, enabled])
}

export function useSystemStatus() {
  const [status,  setStatus]  = useState<SystemStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState<string | null>(null)

  const fetch = async () => {
    try {
      setStatus(await systemApi.getStatus())
      setError(null)
    } catch {
      setError('Backend unreachable')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetch() }, [])
  usePolling(fetch, 3000)
  return { status, loading, error }
}

export function useAttendanceToday() {
  const [data,    setData]    = useState<AttendanceToday | null>(null)
  const [loading, setLoading] = useState(true)

  const fetch = useCallback(async () => {
    try   { setData(await attendanceApi.getToday()) }
    catch { /* silent */ }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { fetch() }, [fetch])
  usePolling(fetch, 5000)
  return { data, loading, refetch: fetch }
}

export function useAbsentUsers() {
  const [data,    setData]    = useState<AbsentUsers | null>(null)
  const [loading, setLoading] = useState(true)

  const fetch = useCallback(async () => {
    try   { setData(await attendanceApi.getAbsent()) }
    catch { /* silent */ }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { fetch() }, [fetch])
  usePolling(fetch, 10000)
  return { data, loading }
}
