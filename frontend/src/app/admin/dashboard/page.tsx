'use client'
// src/app/admin/dashboard/page.tsx

import { motion } from 'framer-motion'
import { Users, UserCheck, UserX, Cpu, Activity } from 'lucide-react'
import { AnimatedStatCard, AnimatedTable } from '@/components/shared'
import { useSystemStatus, useAttendanceToday, useAbsentUsers } from '@/hooks'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts'

const weekData = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].map(d => ({
  date: d, count: Math.floor(Math.random() * 20) + 8,
}))

export default function AdminDashboard() {
  const { status, loading: sl } = useSystemStatus()
  const { data: today, loading: tl } = useAttendanceToday()
  const { data: absent } = useAbsentUsers()

  const stats = [
    { label: 'Enrolled Users', value: status?.enrolled_users  ?? '—', icon: Users,     color: 'blue'    as const, delay: 0    },
    { label: 'Present Today',  value: today?.count            ?? '—', icon: UserCheck, color: 'emerald' as const, delay: 0.05 },
    { label: 'Absent Today',   value: absent?.count           ?? '—', icon: UserX,     color: 'red'     as const, delay: 0.1  },
    { label: 'System FPS',     value: status?.fps?.toFixed(1) ?? '—', icon: Cpu,       color: 'purple'  as const, delay: 0.15 },
    { label: 'Avg Latency',    value: status?.avg_latency_ms  ? `${status.avg_latency_ms.toFixed(0)}ms` : '—', icon: Activity, color: 'amber' as const, delay: 0.2 },
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {stats.map(s => <AnimatedStatCard key={s.label} {...s} loading={sl && tl} />)}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          className="lg:col-span-2 rounded-xl bg-zinc-900 border border-zinc-800/50 p-5"
        >
          <p className="text-sm font-medium text-zinc-300 mb-4">Weekly Attendance Trend</p>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={weekData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
                <defs>
                  <linearGradient id="ag" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis dataKey="date" tick={{ fill: '#52525b', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#52525b', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: '#18181b', border: '1px solid #27272a', borderRadius: 8 }} labelStyle={{ color: '#a1a1aa' }} itemStyle={{ color: '#60a5fa' }} />
                <Area type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} fill="url(#ag)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}
          className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-5"
        >
          <p className="text-sm font-medium text-zinc-300 mb-4">System Health</p>
          <div className="space-y-3">
            {[
              { label: 'Camera',      on: status?.camera_active      },
              { label: 'Recognition', on: status?.recognition_active },
              { label: 'Database',    on: true                       },
            ].map(item => (
              <div key={item.label} className="flex items-center justify-between py-2 border-b border-zinc-800/30 last:border-0">
                <span className="text-sm text-zinc-400">{item.label}</span>
                <div className="flex items-center gap-2">
                  <motion.div
                    animate={item.on ? { scale: [1,1.3,1] } : {}}
                    transition={{ repeat: Infinity, duration: 2 }}
                    className={`w-2 h-2 rounded-full ${item.on ? 'bg-emerald-400' : 'bg-zinc-600'}`}
                  />
                  <span className={`text-xs ${item.on ? 'text-emerald-400' : 'text-zinc-500'}`}>
                    {item.on ? 'Online' : 'Offline'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
        className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-5"
      >
        <p className="text-sm font-medium text-zinc-300 mb-4">Recent Attendance</p>
        <AnimatedTable records={today?.records.slice(0,6) ?? []} loading={tl} />
      </motion.div>
    </div>
  )
}
