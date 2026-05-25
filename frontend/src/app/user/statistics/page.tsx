'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '@/context/AuthContext'
import { attendanceApi } from '@/services/api'
import type { AttendanceHistory } from '@/types'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function UserStatisticsPage() {
  const { user }         = useAuth()
  const [hist, setHist]  = useState<AttendanceHistory | null>(null)

  useEffect(() => {
    if (!user?.employee_id) return
    attendanceApi.getHistory({ employee_id: user.employee_id, page_size: 60 }).then(setHist).catch(()=>{})
  }, [user])

  const records   = hist?.records ?? []
  const present   = records.filter(r => r.status==='present').length
  const total     = records.length
  const pct       = total ? Math.round((present/total)*100) : 0

  // Group by month
  const byMonth: Record<string,number> = {}
  records.forEach(r => {
    const m = r.date.slice(0,7)
    byMonth[m] = (byMonth[m]??0) + 1
  })
  const chartData = Object.entries(byMonth).map(([month,count]) => ({ month, count }))

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-4">
        {[
          { label:'Present Days', value:present,  color:'text-emerald-400' },
          { label:'Total Tracked', value:total,   color:'text-blue-400'    },
          { label:'Attendance %',  value:`${pct}%`, color: pct>=80?'text-emerald-400':pct>=60?'text-amber-400':'text-red-400' },
        ].map((s,i) => (
          <motion.div key={s.label}
            initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:i*0.07 }}
            className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-5"
          >
            <p className="text-xs text-zinc-500 mb-2">{s.label}</p>
            <p className={`text-2xl font-bold tabular-nums ${s.color}`}>{s.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Attendance % bar */}
      <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.2 }}
        className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-5"
      >
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm font-medium text-zinc-300">Attendance Rate</p>
          <span className={`text-sm font-bold ${pct>=80?'text-emerald-400':pct>=60?'text-amber-400':'text-red-400'}`}>{pct}%</span>
        </div>
        <div className="h-2.5 bg-zinc-800 rounded-full overflow-hidden">
          <motion.div
            initial={{ width:0 }}
            animate={{ width:`${pct}%` }}
            transition={{ duration:1, ease:'easeOut', delay:0.4 }}
            className={`h-full rounded-full ${pct>=80?'bg-emerald-500':pct>=60?'bg-amber-500':'bg-red-500'}`}
          />
        </div>
      </motion.div>

      {chartData.length > 0 && (
        <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.3 }}
          className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-5"
        >
          <p className="text-sm font-medium text-zinc-300 mb-4">Monthly Trend</p>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top:4, right:4, bottom:0, left:-20 }}>
                <defs>
                  <linearGradient id="ug" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}   />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis dataKey="month" tick={{ fill:'#52525b', fontSize:11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill:'#52525b', fontSize:11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background:'#18181b', border:'1px solid #27272a', borderRadius:8 }} itemStyle={{ color:'#34d399' }} />
                <Area type="monotone" dataKey="count" stroke="#10b981" strokeWidth={2} fill="url(#ug)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      )}
    </div>
  )
}
