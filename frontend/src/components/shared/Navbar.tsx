'use client'
// src/components/shared/Navbar.tsx

import { usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import { useSystemStatus } from '@/hooks'
import { useAuth } from '@/context/AuthContext'
import { cn } from '@/lib/utils'

const titles: Record<string, string> = {
  '/admin/dashboard':   'Dashboard',
  '/admin/recognition': 'Live Recognition',
  '/admin/enrollment':  'Enrollment',
  '/admin/attendance':  'Attendance',
  '/admin/analytics':   'Analytics',
  '/admin/system':      'System Status',
  '/admin/users':       'Users',
  '/user/dashboard':    'My Dashboard',
  '/user/attendance':   'My Attendance',
  '/user/statistics':   'Statistics',
  '/user/export':       'Export',
  '/user/profile':      'Profile',
}

export function Navbar() {
  const pathname    = usePathname()
  const { status }  = useSystemStatus()
  const { user }    = useAuth()
  const title       = titles[pathname] ?? 'FaceAttend'
  const isAdmin     = user?.role === 'admin'

  return (
    <motion.header
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center justify-between px-6 py-4 border-b border-zinc-800/50 bg-zinc-950/80 backdrop-blur-sm shrink-0"
    >
      <motion.h1
        key={pathname}
        initial={{ opacity: 0, x: -8 }}
        animate={{ opacity: 1, x: 0 }}
        className="text-sm font-semibold text-white"
      >
        {title}
      </motion.h1>

      <div className="flex items-center gap-3">
        {isAdmin && status && (
          <>
            <div className="flex items-center gap-2">
              <motion.div
                animate={{ scale: [1, 1.3, 1] }}
                transition={{ repeat: Infinity, duration: 2 }}
                className={cn('w-2 h-2 rounded-full', status.recognition_active ? 'bg-emerald-400' : 'bg-zinc-600')}
              />
              <span className="text-xs text-zinc-500 hidden sm:block">
                {status.recognition_active ? 'Active' : 'Idle'}
              </span>
            </div>
            <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
              <span className="text-xs text-zinc-400">FPS</span>
              <span className="text-xs font-mono font-semibold text-blue-400">
                {status.fps?.toFixed(1) ?? '—'}
              </span>
            </div>
          </>
        )}
        <div className="flex items-center gap-2">
          <div className={cn(
            'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold',
            isAdmin
              ? 'bg-purple-500/20 border border-purple-500/30 text-purple-400'
              : 'bg-emerald-500/20 border border-emerald-500/30 text-emerald-400'
          )}>
            {user?.name?.charAt(0) ?? '?'}
          </div>
        </div>
      </div>
    </motion.header>
  )
}
