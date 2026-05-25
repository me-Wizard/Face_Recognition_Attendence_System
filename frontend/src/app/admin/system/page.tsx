'use client'
// src/app/admin/system/page.tsx

import { motion } from 'framer-motion'
import { Activity, Cpu, Clock, Database, Camera, Zap } from 'lucide-react'
import { SystemMetricCard } from '@/components/shared'
import { useSystemStatus } from '@/hooks'

export default function SystemPage() {
  const { status, error } = useSystemStatus()

  if (error) return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <div className="w-12 h-12 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto mb-3">
          <Zap className="w-5 h-5 text-red-400" />
        </div>
        <p className="text-sm font-medium text-red-400">Backend Unreachable</p>
        <p className="text-xs text-zinc-600 mt-1">Make sure uvicorn is running on port 8000</p>
      </div>
    </div>
  )

  const services = [
    { label: 'Camera',      on: status?.camera_active,      icon: Camera   },
    { label: 'Recognition', on: status?.recognition_active, icon: Activity },
    { label: 'Database',    on: true,                       icon: Database },
  ]

  const metrics = [
    { label: 'FPS',           value: status?.fps?.toFixed(1)??'—',            unit:'fps', icon:Cpu,      status:(status?.fps??0)>15?'good' as const:'warn' as const,                              delay:0     },
    { label: 'Avg Latency',   value: status?.avg_latency_ms?.toFixed(0)??'—', unit:'ms',  icon:Clock,    status:(status?.avg_latency_ms??999)<100?'good' as const:'warn' as const,                delay:0.05  },
    { label: 'Total Frames',  value: status?.total_frames??'—',               unit:'',    icon:Activity, status:'good' as const,                                                                   delay:0.1   },
    { label: 'Processed',     value: status?.processed_frames??'—',           unit:'',    icon:Zap,      status:'good' as const,                                                                   delay:0.15  },
    { label: 'Enrolled',      value: status?.enrolled_users??'—',             unit:'',    icon:Database, status:'good' as const,                                                                   delay:0.2   },
    { label: 'Present Today', value: status?.attendance_today??'—',           unit:'',    icon:Camera,   status:'good' as const,                                                                   delay:0.25  },
  ]

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {services.map((s,i) => (
          <motion.div key={s.label}
            initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:i*0.07 }}
            className="flex items-center justify-between p-4 rounded-xl bg-zinc-900 border border-zinc-800/50"
          >
            <div className="flex items-center gap-3">
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center border ${s.on?'bg-emerald-500/10 border-emerald-500/20':'bg-zinc-800 border-zinc-700/50'}`}>
                <s.icon className={`w-4 h-4 ${s.on?'text-emerald-400':'text-zinc-600'}`} />
              </div>
              <span className="text-sm font-medium text-white">{s.label}</span>
            </div>
            <div className="flex items-center gap-2">
              <motion.div
                animate={s.on?{scale:[1,1.3,1]}:{}}
                transition={{ repeat:Infinity, duration:2 }}
                className={`w-2 h-2 rounded-full ${s.on?'bg-emerald-400':'bg-zinc-600'}`}
              />
              <span className={`text-xs ${s.on?'text-emerald-400':'text-zinc-500'}`}>
                {s.on?'Online':'Offline'}
              </span>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {metrics.map(m => <SystemMetricCard key={m.label} {...m} />)}
      </div>

      {status && (
        <motion.div initial={{ opacity:0 }} animate={{ opacity:1 }} transition={{ delay:0.4 }}
          className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-5"
        >
          <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-3">Raw API Response</p>
          <pre className="text-xs text-zinc-400 font-mono overflow-auto">{JSON.stringify(status,null,2)}</pre>
        </motion.div>
      )}
    </div>
  )
}
