'use client'
// src/app/admin/recognition/page.tsx

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Play, Scan, Zap, Clock, Cpu, Activity } from 'lucide-react'
import { GlowButton, SystemMetricCard } from '@/components/shared'
import { useSystemStatus, useAttendanceToday } from '@/hooks'
import { recognitionApi, attendanceApi } from '@/services/api'
import type { RecognitionEvent, AttendanceStatus } from '@/types'
import { AnimatePresence as AP } from 'framer-motion'

function RecognitionCard({ event }: { event: RecognitionEvent }) {
  const cfg = {
    success:     { color: 'text-emerald-400', bg: 'bg-emerald-500/5',  border: 'border-emerald-500/20' },
    exists:      { color: 'text-blue-400',    bg: 'bg-blue-500/5',     border: 'border-blue-500/20'   },
    recognizing: { color: 'text-amber-400',   bg: 'bg-amber-500/5',    border: 'border-amber-500/20'  },
    cooldown:    { color: 'text-zinc-400',    bg: 'bg-zinc-800/50',    border: 'border-zinc-700/50'   },
    failed:      { color: 'text-red-400',     bg: 'bg-red-500/5',      border: 'border-red-500/20'    },
  }
  const c = cfg[event.status] ?? cfg.failed

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 16 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -16 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
      className={`flex items-center gap-3 p-3 rounded-xl border ${c.bg} ${c.border}`}
    >
      <div className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center shrink-0">
        <span className="text-xs font-bold text-white">
          {event.name?.charAt(0) ?? '?'}
        </span>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-white truncate">{event.name ?? 'Unknown'}</p>
        <p className="text-xs text-zinc-500 truncate">{event.message}</p>
      </div>
      {event.confidence != null && (
        <span className={`text-xs font-mono ${c.color}`}>
          {(event.confidence * 100).toFixed(0)}%
        </span>
      )}
    </motion.div>
  )
}

export default function RecognitionPage() {
  const [running,    setRunning]    = useState(false)
  const [loading,    setLoading]    = useState(false)
  const [events,     setEvents]     = useState<RecognitionEvent[]>([])
  const [attStatus,  setAttStatus]  = useState<AttendanceStatus | null>(null)
  const { status }                  = useSystemStatus()
  const { data: today }             = useAttendanceToday()

  const fetchStatus = useCallback(async () => {
    try { setAttStatus(await attendanceApi.getStatus()) } catch {}
  }, [])

  useEffect(() => {
    fetchStatus()
    const id = setInterval(fetchStatus, 3000)
    return () => clearInterval(id)
  }, [fetchStatus])

  const start = async () => {
    setLoading(true)
    try {
      await recognitionApi.startLoop()
      setRunning(true)
    } catch {
      setRunning(false)
    } finally {
      setLoading(false)
    }
  }

  const poll = useCallback(async () => {
    if (!running) return
    try {
      const data = await attendanceApi.getToday()
      setEvents(data.records.slice(0, 8).map(r => ({
        id: r.attendance_id.toString(),
        status: 'exists' as const,
        message: 'Marked Present',
        name: r.name,
        employee_id: r.employee_id,
        timestamp: new Date(),
      })))
    } catch {}
  }, [running])

  useEffect(() => {
    if (!running) return
    const id = setInterval(poll, 4000)
    return () => clearInterval(id)
  }, [running, poll])

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-4">
        {/* Camera panel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative rounded-xl bg-zinc-900 border border-zinc-800/50 overflow-hidden"
          style={{ minHeight: 340 }}
        >
          {running && (
            <motion.div
              animate={{ y: ['0%','100%','0%'] }}
              transition={{ repeat: Infinity, duration: 4, ease: 'linear' }}
              className="absolute inset-x-0 h-px bg-blue-500/20 pointer-events-none"
            />
          )}
          {['top-0 left-0','top-0 right-0','bottom-0 left-0','bottom-0 right-0'].map((p,i) => (
            <div key={i} className={`absolute ${p} w-5 h-5 m-3 ${
              i===0?'border-t border-l':i===1?'border-t border-r':i===2?'border-b border-l':'border-b border-r'
            } border-blue-500/30`} />
          ))}

          <div className="absolute inset-0 flex flex-col items-center justify-center gap-4">
            <AnimatePresence mode="wait">
              {running ? (
                <motion.div key="running" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
                  className="flex flex-col items-center gap-3"
                >
                  <motion.div
                    animate={{ scale:[1,1.1,1], opacity:[1,0.7,1] }}
                    transition={{ repeat: Infinity, duration: 2 }}
                    className="w-14 h-14 rounded-full bg-blue-500/10 border border-blue-500/30 flex items-center justify-center"
                  >
                    <Scan className="w-6 h-6 text-blue-400" />
                  </motion.div>
                  <p className="text-sm font-medium text-blue-400">Recognition active</p>
                  <p className="text-xs text-zinc-500">Camera running on server — press Q in camera window to stop</p>
                </motion.div>
              ) : (
                <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                  className="flex flex-col items-center gap-4"
                >
                  <div className="w-14 h-14 rounded-full bg-zinc-800/50 border border-zinc-700/50 flex items-center justify-center">
                    <Scan className="w-6 h-6 text-zinc-600" />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-medium text-zinc-300">Camera Inactive</p>
                    <p className="text-xs text-zinc-600 mt-1">Start recognition to activate</p>
                  </div>
                  <GlowButton onClick={start} loading={loading}>
                    <Play className="w-4 h-4" /> Start Recognition
                  </GlowButton>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {running && (
            <div className="absolute top-3 right-3 flex items-center gap-1.5">
              <motion.div animate={{ scale:[1,1.3,1] }} transition={{ repeat: Infinity, duration: 1.5 }}
                className="w-2 h-2 rounded-full bg-red-500" />
              <span className="text-xs font-medium text-red-400">LIVE</span>
            </div>
          )}
        </motion.div>

        {/* Metrics */}
        <div className="grid grid-cols-3 gap-4">
          <SystemMetricCard label="FPS" value={status?.fps?.toFixed(1)??'—'} icon={Cpu}
            status={(status?.fps??0)>15?'good':'warn'} delay={0.1} />
          <SystemMetricCard label="Latency" value={status?.avg_latency_ms?.toFixed(0)??'—'} unit="ms" icon={Clock}
            status={(status?.avg_latency_ms??999)<100?'good':'warn'} delay={0.15} />
          <SystemMetricCard label="Present Today" value={today?.count??0} icon={Activity}
            status="good" delay={0.2} />
        </div>

        {attStatus && attStatus.users_in_cooldown.length > 0 && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="rounded-xl bg-amber-500/5 border border-amber-500/20 p-3 flex items-center gap-2"
          >
            <Zap className="w-4 h-4 text-amber-400 shrink-0" />
            <p className="text-xs text-zinc-400">
              Cooldown: <span className="text-amber-400">{attStatus.users_in_cooldown.join(', ')}</span>
            </p>
          </motion.div>
        )}
      </div>

      {/* Live feed */}
      <motion.div
        initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
        className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-4 overflow-y-auto"
        style={{ maxHeight: 'calc(100vh - 140px)' }}
      >
        <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-3">Live Activity</p>
        <div className="space-y-2">
          <AP mode="popLayout">
            {events.length === 0 ? (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="flex flex-col items-center justify-center py-12 text-zinc-600"
              >
                <motion.div animate={{ scale:[1,1.2,1] }} transition={{ repeat: Infinity, duration: 2 }}
                  className="w-10 h-10 rounded-full bg-zinc-800/50 flex items-center justify-center mb-3"
                >
                  <div className="w-3 h-3 rounded-full bg-zinc-700" />
                </motion.div>
                <p className="text-sm">Waiting for detections...</p>
              </motion.div>
            ) : events.map(e => <RecognitionCard key={e.id} event={e} />)}
          </AP>
        </div>
      </motion.div>
    </div>
  )
}
