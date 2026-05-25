'use client'
import { motion } from 'framer-motion'
import { CalendarCheck, CalendarX, Percent, Clock } from 'lucide-react'
import { AnimatedStatCard, AnimatedTable } from '@/components/shared'
import { useAuth } from '@/context/AuthContext'
import { useAttendanceToday } from '@/hooks'
import { useState, useEffect } from 'react'
import { attendanceApi } from '@/services/api'
import type { AttendanceHistory } from '@/types'

export default function UserDashboard() {
  const { user }             = useAuth()
  const { data: today }      = useAttendanceToday()
  const [hist, setHist]      = useState<AttendanceHistory | null>(null)

  useEffect(() => {
    if (!user?.employee_id) return
    attendanceApi.getHistory({ employee_id: user.employee_id, page_size: 30 })
      .then(setHist).catch(() => {})
  }, [user])

  const myRecords  = hist?.records ?? []
  const presentCt  = myRecords.filter(r => r.status === 'present').length
  const totalDays  = myRecords.length
  const pct        = totalDays ? Math.round((presentCt / totalDays) * 100) : 0
  const myToday    = today?.records.find(r => r.employee_id === user?.employee_id)

  const stats = [
    { label: 'Days Present',  value: presentCt,          icon: CalendarCheck, color: 'emerald' as const, delay: 0    },
    { label: 'Days Absent',   value: totalDays-presentCt, icon: CalendarX,     color: 'red'     as const, delay: 0.05 },
    { label: 'Attendance %',  value: `${pct}%`,           icon: Percent,       color: 'blue'    as const, delay: 0.1  },
    { label: 'Today Status',  value: myToday ? 'Present' : 'Not Yet', icon: Clock, color: myToday ? 'emerald' as const : 'amber' as const, delay: 0.15 },
  ]

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity:0, y:-10 }} animate={{ opacity:1, y:0 }}
        className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-5"
      >
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
            <span className="text-lg font-bold text-emerald-400">{user?.name?.charAt(0)}</span>
          </div>
          <div>
            <p className="font-semibold text-white">{user?.name}</p>
            <p className="text-xs text-zinc-500">{user?.employee_id} · {user?.email}</p>
          </div>
          {myToday && (
            <div className="ml-auto flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
              <motion.div animate={{ scale:[1,1.3,1] }} transition={{ repeat:Infinity, duration:2 }}
                className="w-2 h-2 rounded-full bg-emerald-400" />
              <span className="text-xs text-emerald-400 font-medium">Present Today</span>
            </div>
          )}
        </div>
      </motion.div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(s => <AnimatedStatCard key={s.label} {...s} />)}
      </div>

      <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.3 }}
        className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-5"
      >
        <p className="text-sm font-medium text-zinc-300 mb-4">Recent Attendance</p>
        <AnimatedTable records={myRecords.slice(0,8)} compact />
      </motion.div>
    </div>
  )
}
