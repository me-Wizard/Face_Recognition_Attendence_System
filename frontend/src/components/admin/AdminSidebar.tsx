'use client'
// src/components/admin/AdminSidebar.tsx

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard, Camera, UserPlus, ClipboardList,
  BarChart3, Activity, Users, Settings,
  ChevronLeft, ChevronRight, Scan, LogOut,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/context/AuthContext'

const nav = [
  { href: '/admin/dashboard',   icon: LayoutDashboard, label: 'Dashboard'   },
  { href: '/admin/recognition', icon: Camera,           label: 'Recognition' },
  { href: '/admin/enrollment',  icon: UserPlus,         label: 'Enrollment'  },
  { href: '/admin/attendance',  icon: ClipboardList,    label: 'Attendance'  },
  { href: '/admin/analytics',   icon: BarChart3,        label: 'Analytics'   },
  { href: '/admin/system',      icon: Activity,         label: 'System'      },
  { href: '/admin/users',       icon: Users,            label: 'Users'       },
]

export function AdminSidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const pathname                  = usePathname()
  const { user, logout }          = useAuth()

  return (
    <motion.aside
      animate={{ width: collapsed ? 72 : 240 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className="relative flex flex-col h-screen bg-zinc-950 border-r border-zinc-800/50 overflow-hidden shrink-0 z-10"
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-zinc-800/50">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 shrink-0">
          <Scan className="w-4 h-4 text-blue-400" />
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.15 }}
            >
              <p className="text-sm font-bold text-white">FaceAttend</p>
              <p className="text-xs text-purple-400">Admin Panel</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-4 space-y-0.5 overflow-y-auto">
        {nav.map((item, i) => {
          const active = pathname.startsWith(item.href)
          return (
            <motion.div
              key={item.href}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.04 }}
            >
              <Link href={item.href}>
                <motion.div
                  whileHover={{ x: 2 }}
                  whileTap={{ scale: 0.97 }}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors relative',
                    active
                      ? 'text-blue-400'
                      : 'text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800/50'
                  )}
                >
                  {active && (
                    <motion.div
                      layoutId="adminNav"
                      className="absolute inset-0 rounded-lg bg-blue-500/10 border border-blue-500/20"
                      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                    />
                  )}
                  <item.icon className="w-4 h-4 shrink-0 relative z-10" />
                  <AnimatePresence>
                    {!collapsed && (
                      <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="text-sm font-medium whitespace-nowrap relative z-10"
                      >
                        {item.label}
                      </motion.span>
                    )}
                  </AnimatePresence>
                </motion.div>
              </Link>
            </motion.div>
          )
        })}
      </nav>

      {/* User + logout */}
      <div className="px-2 pb-2 border-t border-zinc-800/50 pt-2">
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-2 px-3 py-2 mb-1"
            >
              <div className="w-6 h-6 rounded-full bg-purple-500/20 border border-purple-500/30 flex items-center justify-center shrink-0">
                <span className="text-xs font-bold text-purple-400">
                  {user?.name?.charAt(0) ?? 'A'}
                </span>
              </div>
              <div className="min-w-0">
                <p className="text-xs font-medium text-white truncate">{user?.name}</p>
                <p className="text-xs text-zinc-600 truncate">{user?.email}</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.97 }}
          onClick={logout}
          className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-zinc-500 hover:text-red-400 hover:bg-red-500/5 transition-colors"
        >
          <LogOut className="w-4 h-4 shrink-0" />
          <AnimatePresence>
            {!collapsed && (
              <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="text-sm">Sign out</motion.span>
            )}
          </AnimatePresence>
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.02 }}
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center justify-center w-full h-8 mt-1 rounded-lg text-zinc-600 hover:text-zinc-400 hover:bg-zinc-800/50 transition-colors"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </motion.button>
      </div>
    </motion.aside>
  )
}
