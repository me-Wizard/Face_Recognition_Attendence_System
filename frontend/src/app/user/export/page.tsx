'use client'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { Download, FileText } from 'lucide-react'
import { GlowButton } from '@/components/shared'
import { attendanceApi } from '@/services/api'
import { downloadBlob } from '@/lib/utils'

export default function UserExportPage() {
  const [loading, setLoading] = useState(false)
  const [done,    setDone]    = useState(false)

  const doExport = async () => {
    setLoading(true); setDone(false)
    try {
      const blob = await attendanceApi.exportCsv()
      downloadBlob(blob, `my_attendance_${new Date().toISOString().split('T')[0]}.csv`)
      setDone(true)
    } finally { setLoading(false) }
  }

  return (
    <div className="max-w-md mx-auto">
      <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }}
        className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-8 text-center"
      >
        <div className="w-14 h-14 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mx-auto mb-5">
          <FileText className="w-6 h-6 text-emerald-400" />
        </div>
        <p className="text-base font-semibold text-white mb-2">Export Attendance</p>
        <p className="text-sm text-zinc-500 mb-6">Download your attendance records as a CSV file.</p>

        <GlowButton onClick={doExport} loading={loading} className="mx-auto">
          <Download className="w-4 h-4" /> Download CSV
        </GlowButton>

        {done && (
          <motion.p initial={{ opacity:0 }} animate={{ opacity:1 }}
            className="mt-4 text-xs text-emerald-400"
          >
            File downloaded successfully.
          </motion.p>
        )}
      </motion.div>
    </div>
  )
}
