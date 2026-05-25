'use client'
// src/components/shared/index.tsx

import { motion, AnimatePresence } from 'framer-motion'
import { type LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'
import { formatTime } from '@/lib/utils'
import type { AttendanceRecord } from '@/types'
import { type ReactNode } from 'react'

// ── GlowButton ────────────────────────────────────────────────────────────────

interface BtnProps {
  children: ReactNode
  onClick?: () => void
  variant?: 'primary' | 'ghost' | 'danger'
  loading?: boolean
  disabled?: boolean
  className?: string
  type?: 'button' | 'submit'
  size?: 'sm' | 'md'
}

export function GlowButton({
  children, onClick, variant = 'primary',
  loading, disabled, className, type = 'button', size = 'md',
}: BtnProps) {
  const v = {
    primary: 'bg-blue-600 hover:bg-blue-500 text-white border-blue-500/50 hover:shadow-blue-500/20',
    ghost:   'bg-zinc-800/50 hover:bg-zinc-700/50 text-zinc-300 border-zinc-700/50',
    danger:  'bg-red-600/20 hover:bg-red-600/30 text-red-400 border-red-500/30',
  }
  const s = size === 'sm' ? 'px-3 py-1.5 text-xs' : 'px-4 py-2 text-sm'

  return (
    <motion.button
      type={type}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.97 }}
      onClick={onClick}
      disabled={disabled || loading}
      className={cn(
        'flex items-center gap-2 rounded-lg font-medium border transition-all hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed',
        v[variant], s, className
      )}
    >
      {loading ? (
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
          className="w-4 h-4 border-2 border-current border-t-transparent rounded-full"
        />
      ) : children}
    </motion.button>
  )
}

// ── StatusBadge ───────────────────────────────────────────────────────────────

const badgeCfg: Record<string, { label: string; cls: string }> = {
  success:     { label: 'Marked',   cls: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' },
  exists:      { label: 'Present',  cls: 'bg-blue-500/10 text-blue-400 border-blue-500/20'         },
  recognizing: { label: 'Scanning', cls: 'bg-amber-500/10 text-amber-400 border-amber-500/20'      },
  cooldown:    { label: 'Cooldown', cls: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20'         },
  failed:      { label: 'Unknown',  cls: 'bg-red-500/10 text-red-400 border-red-500/20'            },
  present:     { label: 'Present',  cls: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'},
  absent:      { label: 'Absent',   cls: 'bg-red-500/10 text-red-400 border-red-500/20'            },
  admin:       { label: 'Admin',    cls: 'bg-purple-500/10 text-purple-400 border-purple-500/20'   },
  user:        { label: 'User',     cls: 'bg-blue-500/10 text-blue-400 border-blue-500/20'         },
}

export function StatusBadge({ status }: { status: string }) {
  const c = badgeCfg[status] ?? badgeCfg.failed
  return (
    <span className={cn('inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border', c.cls)}>
      {c.label}
    </span>
  )
}

// ── AnimatedStatCard ──────────────────────────────────────────────────────────

interface StatProps {
  label:    string
  value:    string | number
  icon:     LucideIcon
  color?:   'blue' | 'emerald' | 'red' | 'amber' | 'purple'
  delay?:   number
  loading?: boolean
  sub?:     string
}

const colorMap = {
  blue:    { icon: 'text-blue-400',    bg: 'bg-blue-500/10',    border: 'border-blue-500/20'    },
  emerald: { icon: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' },
  red:     { icon: 'text-red-400',     bg: 'bg-red-500/10',     border: 'border-red-500/20'     },
  amber:   { icon: 'text-amber-400',   bg: 'bg-amber-500/10',   border: 'border-amber-500/20'   },
  purple:  { icon: 'text-purple-400',  bg: 'bg-purple-500/10',  border: 'border-purple-500/20'  },
}

export function AnimatedStatCard({ label, value, icon: Icon, color = 'blue', delay = 0, loading, sub }: StatProps) {
  const c = colorMap[color]
  if (loading) return (
    <div className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-5 animate-pulse">
      <div className="w-8 h-8 rounded-lg bg-zinc-800 mb-4" />
      <div className="w-16 h-6 bg-zinc-800 rounded mb-2" />
      <div className="w-24 h-3 bg-zinc-800 rounded" />
    </div>
  )
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, type: 'spring', stiffness: 200, damping: 20 }}
      whileHover={{ y: -2 }}
      className={cn('rounded-xl bg-zinc-900 border p-5 cursor-default', c.border)}
    >
      <div className={cn('flex items-center justify-center w-9 h-9 rounded-lg mb-4', c.bg)}>
        <Icon className={cn('w-4 h-4', c.icon)} />
      </div>
      <p className="text-2xl font-bold text-white tabular-nums">{value}</p>
      <p className="text-xs text-zinc-500 mt-1">{label}</p>
      {sub && <p className="text-xs text-emerald-400 mt-2">{sub}</p>}
    </motion.div>
  )
}

// ── SystemMetricCard ──────────────────────────────────────────────────────────

interface MetricProps {
  label:   string
  value:   string | number
  unit?:   string
  icon:    LucideIcon
  status?: 'good' | 'warn' | 'bad'
  delay?:  number
}

export function SystemMetricCard({ label, value, unit, icon: Icon, status = 'good', delay = 0 }: MetricProps) {
  const sc = { good: 'text-emerald-400', warn: 'text-amber-400', bad: 'text-red-400' }
  const bw = { good: '80%', warn: '50%', bad: '20%' }
  const bc = { good: 'bg-emerald-500', warn: 'bg-amber-500', bad: 'bg-red-500' }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, type: 'spring', stiffness: 200 }}
      className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-4"
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-zinc-500">{label}</span>
        <Icon className="w-3.5 h-3.5 text-zinc-600" />
      </div>
      <div className="flex items-baseline gap-1">
        <span className={cn('text-xl font-bold tabular-nums', sc[status])}>{value}</span>
        {unit && <span className="text-xs text-zinc-600">{unit}</span>}
      </div>
      <div className="mt-3 h-1 bg-zinc-800 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: bw[status] }}
          transition={{ delay: delay + 0.2, duration: 0.8, ease: 'easeOut' }}
          className={cn('h-full rounded-full', bc[status])}
        />
      </div>
    </motion.div>
  )
}

// ── AnimatedTable ─────────────────────────────────────────────────────────────

interface TableProps {
  records:  AttendanceRecord[]
  loading?: boolean
  compact?: boolean
}

export function AnimatedTable({ records, loading, compact }: TableProps) {
  if (loading) return (
    <div className="space-y-2">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="h-12 rounded-lg bg-zinc-900 animate-pulse" />
      ))}
    </div>
  )

  if (!records.length) return (
    <div className="flex flex-col items-center justify-center py-16 text-zinc-600">
      <p className="text-sm">No records found</p>
    </div>
  )

  return (
    <div className="overflow-hidden rounded-xl border border-zinc-800/50">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-zinc-800/50 bg-zinc-900/50">
            {['Name', 'Employee ID', ...(compact ? [] : ['Department']), 'Time', 'Status'].map(h => (
              <th key={h} className="px-4 py-3 text-left text-xs font-medium text-zinc-500 uppercase tracking-wider">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <AnimatePresence>
            {records.map((r, i) => (
              <motion.tr
                key={r.attendance_id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.03 }}
                className="border-b border-zinc-800/30 bg-zinc-950 hover:bg-zinc-900/50 transition-colors"
              >
                <td className="px-4 py-3 font-medium text-white">{r.name}</td>
                <td className="px-4 py-3 text-zinc-400 font-mono text-xs">{r.employee_id}</td>
                {!compact && <td className="px-4 py-3 text-zinc-400">{r.department}</td>}
                <td className="px-4 py-3 text-zinc-400 font-mono text-xs">{formatTime(r.time)}</td>
                <td className="px-4 py-3"><StatusBadge status={r.status} /></td>
              </motion.tr>
            ))}
          </AnimatePresence>
        </tbody>
      </table>
    </div>
  )
}
