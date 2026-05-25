'use client'
// src/app/admin/attendance/page.tsx

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Search, Download, Filter } from 'lucide-react'
import { AnimatedTable, GlowButton } from '@/components/shared'
import { attendanceApi } from '@/services/api'
import { downloadBlob } from '@/lib/utils'
import type { AttendanceHistory } from '@/types'

export default function AdminAttendancePage() {
  const [data,     setData]     = useState<AttendanceHistory | null>(null)
  const [loading,  setLoading]  = useState(true)
  const [search,   setSearch]   = useState('')
  const [page,     setPage]     = useState(1)
  const [exporting,setExp]      = useState(false)
  const [from,     setFrom]     = useState('')
  const [to,       setTo]       = useState('')

  const fetch = async () => {
    setLoading(true)
    try {
      setData(await attendanceApi.getHistory({
        employee_id: search || undefined,
        from_date: from || undefined,
        to_date: to || undefined,
        page, page_size: 15,
      }))
    } finally { setLoading(false) }
  }

  useEffect(() => { fetch() }, [page])

  const doExport = async () => {
    setExp(true)
    try {
      const blob = await attendanceApi.exportCsv()
      downloadBlob(blob, `attendance_${new Date().toISOString().split('T')[0]}.csv`)
    } finally { setExp(false) }
  }

  return (
    <div className="space-y-5">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
        className="flex flex-wrap items-center gap-3 p-4 rounded-xl bg-zinc-900 border border-zinc-800/50"
      >
        <div className="flex items-center gap-2 flex-1 min-w-44 px-3 py-2 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
          <Search className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
          <input
            type="text" value={search} onChange={e => setSearch(e.target.value)}
            onKeyDown={e => e.key==='Enter' && (setPage(1), fetch())}
            placeholder="Filter by employee ID..."
            className="flex-1 bg-transparent text-sm text-white placeholder-zinc-600 focus:outline-none"
          />
        </div>
        <input type="date" value={from} onChange={e => setFrom(e.target.value)}
          className="px-3 py-2 rounded-lg bg-zinc-800/50 border border-zinc-700/50 text-sm text-zinc-400 focus:outline-none" />
        <input type="date" value={to} onChange={e => setTo(e.target.value)}
          className="px-3 py-2 rounded-lg bg-zinc-800/50 border border-zinc-700/50 text-sm text-zinc-400 focus:outline-none" />
        <GlowButton variant="ghost" onClick={() => { setPage(1); fetch() }}>
          <Filter className="w-3.5 h-3.5" /> Filter
        </GlowButton>
        <GlowButton variant="ghost" onClick={doExport} loading={exporting}>
          <Download className="w-3.5 h-3.5" /> Export CSV
        </GlowButton>
      </motion.div>

      {data && (
        <p className="text-xs text-zinc-500">{data.total} records — page {data.page} of {data.pages}</p>
      )}

      <AnimatedTable records={data?.records ?? []} loading={loading} />

      {data && data.pages > 1 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center justify-center gap-3">
          <GlowButton variant="ghost" size="sm" onClick={() => setPage(p => Math.max(1,p-1))} disabled={page===1}>Previous</GlowButton>
          <span className="text-sm text-zinc-500">{page} / {data.pages}</span>
          <GlowButton variant="ghost" size="sm" onClick={() => setPage(p => Math.min(data.pages,p+1))} disabled={page===data.pages}>Next</GlowButton>
        </motion.div>
      )}
    </div>
  )
}
