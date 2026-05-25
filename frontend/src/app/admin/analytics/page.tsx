'use client'
// src/app/admin/analytics/page.tsx

import { motion } from 'framer-motion'
import { useAttendanceToday, useAbsentUsers } from '@/hooks'
import { useSystemStatus } from '@/hooks'
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'

const COLORS = ['#10b981','#ef4444','#3b82f6','#f59e0b','#8b5cf6']

export default function AnalyticsPage() {
  const { data: today  } = useAttendanceToday()
  const { data: absent } = useAbsentUsers()
  const { status       } = useSystemStatus()

  const presentCount = today?.count  ?? 0
  const absentCount  = absent?.count ?? 0
  const total        = presentCount + absentCount

  const pieData = [
    { name: 'Present', value: presentCount },
    { name: 'Absent',  value: absentCount  },
  ]

  const deptMap: Record<string,number> = {}
  today?.records.forEach(r => { deptMap[r.department] = (deptMap[r.department]??0)+1 })
  const deptData = Object.entries(deptMap).map(([dept,count])=>({dept,count}))

  const cards = [
    { label: 'Total Enrolled', value: status?.enrolled_users ?? 0,     color: 'text-blue-400'    },
    { label: 'Present Today',  value: presentCount,                     color: 'text-emerald-400' },
    { label: 'Absent Today',   value: absentCount,                      color: 'text-red-400'     },
    { label: 'Attendance %',   value: total ? `${Math.round((presentCount/total)*100)}%` : '—', color: 'text-purple-400' },
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((c,i) => (
          <motion.div key={c.label}
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i*0.07 }}
            className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-5"
          >
            <p className="text-xs text-zinc-500 mb-2">{c.label}</p>
            <p className={`text-2xl font-bold tabular-nums ${c.color}`}>{c.value}</p>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-5"
        >
          <p className="text-sm font-medium text-zinc-300 mb-4">Attendance Split</p>
          <div className="flex items-center gap-6">
            <ResponsiveContainer width={160} height={160}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} dataKey="value" strokeWidth={0}>
                  <Cell fill="#10b981" />
                  <Cell fill="#ef4444" />
                </Pie>
                <Tooltip contentStyle={{ background:'#18181b', border:'1px solid #27272a', borderRadius:8 }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-3">
              {pieData.map((d,i) => (
                <div key={d.name} className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ background: i===0?'#10b981':'#ef4444' }} />
                  <span className="text-xs text-zinc-400">{d.name}</span>
                  <span className="text-xs font-bold text-white ml-2">{d.value}</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}
          className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-5"
        >
          <p className="text-sm font-medium text-zinc-300 mb-4">By Department</p>
          {deptData.length > 0 ? (
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={deptData} margin={{ top:4, right:4, bottom:0, left:-20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis dataKey="dept" tick={{ fill:'#52525b', fontSize:11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill:'#52525b', fontSize:11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background:'#18181b', border:'1px solid #27272a', borderRadius:8 }} itemStyle={{ color:'#818cf8' }} />
                <Bar dataKey="count" radius={[4,4,0,0]}>
                  {deptData.map((_,i) => <Cell key={i} fill={COLORS[i%COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-40 text-zinc-600 text-sm">No data yet</div>
          )}
        </motion.div>
      </div>
    </div>
  )
}
