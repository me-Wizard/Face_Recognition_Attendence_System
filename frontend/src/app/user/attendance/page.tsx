'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { AnimatedTable, GlowButton } from '@/components/shared'
import { attendanceApi } from '@/services/api'
import { useAuth } from '@/context/AuthContext'
import type { AttendanceHistory } from '@/types'

export default function UserAttendancePage() {
  const { user }              = useAuth()
  const [data,    setData]    = useState<AttendanceHistory | null>(null)
  const [loading, setLoading] = useState(true)
  const [page,    setPage]    = useState(1)

  useEffect(() => {
    if (!user?.employee_id) return
    setLoading(true)
    attendanceApi.getHistory({ employee_id: user.employee_id, page, page_size: 15 })
      .then(setData).finally(() => setLoading(false))
  }, [user, page])

  return (
    <div className="space-y-5">
      <motion.div initial={{ opacity:0 }} animate={{ opacity:1 }}
        className="p-4 rounded-xl bg-zinc-900 border border-zinc-800/50"
      >
        <p className="text-sm text-zinc-400">
          Showing attendance for <span className="text-white font-medium">{user?.name}</span>
          {data && <span className="text-zinc-500"> — {data.total} total records</span>}
        </p>
      </motion.div>

      <AnimatedTable records={data?.records ?? []} loading={loading} compact />

      {data && data.pages > 1 && (
        <div className="flex items-center justify-center gap-3">
          <GlowButton variant="ghost" size="sm" onClick={() => setPage(p=>Math.max(1,p-1))} disabled={page===1}>Previous</GlowButton>
          <span className="text-sm text-zinc-500">{page} / {data.pages}</span>
          <GlowButton variant="ghost" size="sm" onClick={() => setPage(p=>Math.min(data.pages,p+1))} disabled={page===data.pages}>Next</GlowButton>
        </div>
      )}
    </div>
  )
}
