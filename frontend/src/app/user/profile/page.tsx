'use client'
import { motion } from 'framer-motion'
import { User, Mail, Badge, Building } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { StatusBadge, GlowButton } from '@/components/shared'

export default function UserProfilePage() {
  const { user, logout } = useAuth()

  const fields = [
    { icon: User,     label: 'Full Name',    value: user?.name        },
    { icon: Mail,     label: 'Email',        value: user?.email       },
    { icon: Badge,    label: 'Employee ID',  value: user?.employee_id ?? '—' },
    { icon: Building, label: 'Role',         value: user?.role        },
  ]

  return (
    <div className="max-w-md mx-auto space-y-5">
      {/* Avatar card */}
      <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }}
        className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-6 flex flex-col items-center"
      >
        <div className="w-16 h-16 rounded-full bg-emerald-500/10 border-2 border-emerald-500/30 flex items-center justify-center mb-4">
          <span className="text-2xl font-bold text-emerald-400">{user?.name?.charAt(0)}</span>
        </div>
        <p className="text-base font-semibold text-white">{user?.name}</p>
        <div className="mt-2"><StatusBadge status={user?.role ?? 'user'} /></div>
      </motion.div>

      {/* Info fields */}
      <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.1 }}
        className="rounded-xl bg-zinc-900 border border-zinc-800/50 divide-y divide-zinc-800/50"
      >
        {fields.map((f,i) => (
          <motion.div key={f.label}
            initial={{ opacity:0, x:-10 }} animate={{ opacity:1, x:0 }} transition={{ delay:i*0.06 }}
            className="flex items-center gap-4 p-4"
          >
            <div className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center shrink-0">
              <f.icon className="w-4 h-4 text-zinc-500" />
            </div>
            <div>
              <p className="text-xs text-zinc-500">{f.label}</p>
              <p className="text-sm font-medium text-white">{f.value}</p>
            </div>
          </motion.div>
        ))}
      </motion.div>

      <GlowButton variant="danger" onClick={logout} className="w-full justify-center">
        Sign Out
      </GlowButton>
    </div>
  )
}
