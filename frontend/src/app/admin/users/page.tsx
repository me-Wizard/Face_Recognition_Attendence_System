'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { UserPlus, Loader2 } from 'lucide-react'
import { StatusBadge, GlowButton } from '@/components/shared'
import { authApi } from '@/services/api'
import type { AdminAccount } from '@/types'

export default function UsersPage() {
  const [users,   setUsers]   = useState<AdminAccount[]>([])
  const [loading, setLoading] = useState(true)
  const [form,    setForm]    = useState({ name:'', email:'', password:'', role:'user', employee_id:'' })
  const [saving,  setSaving]  = useState(false)
  const [msg,     setMsg]     = useState('')

  useEffect(() => {
    authApi.listUsers().then(setUsers).finally(() => setLoading(false))
  }, [])

  const create = async () => {
    setSaving(true); setMsg('')
    try {
      await authApi.register(form)
      setMsg('Account created.')
      setForm({ name:'', email:'', password:'', role:'user', employee_id:'' })
      authApi.listUsers().then(setUsers)
    } catch { setMsg('Failed.') }
    finally { setSaving(false) }
  }

  return (
    <div className="space-y-6">
      {/* Create account */}
      <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }}
        className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-5"
      >
        <p className="text-sm font-semibold text-white mb-4">Create Login Account</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {[
            {k:'name',        ph:'Full Name',   type:'text'    },
            {k:'email',       ph:'Email',       type:'email'   },
            {k:'password',    ph:'Password',    type:'password'},
            {k:'employee_id', ph:'Employee ID (for user role)', type:'text'},
          ].map(f => (
            <input key={f.k} type={f.type} placeholder={f.ph}
              value={form[f.k as keyof typeof form]}
              onChange={e => setForm(p => ({...p,[f.k]:e.target.value}))}
              className="px-3 py-2.5 rounded-lg bg-zinc-800/50 border border-zinc-700/50 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-blue-500/50"
            />
          ))}
          <select value={form.role} onChange={e => setForm(p=>({...p,role:e.target.value}))}
            className="px-3 py-2.5 rounded-lg bg-zinc-800/50 border border-zinc-700/50 text-sm text-white focus:outline-none"
          >
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        <div className="flex items-center gap-3 mt-4">
          <GlowButton onClick={create} loading={saving}>
            <UserPlus className="w-4 h-4" /> Create
          </GlowButton>
          {msg && <p className="text-xs text-emerald-400">{msg}</p>}
        </div>
      </motion.div>

      {/* Users table */}
      <motion.div initial={{ opacity:0 }} animate={{ opacity:1 }} transition={{ delay:0.1 }}
        className="rounded-xl bg-zinc-900 border border-zinc-800/50 overflow-hidden"
      >
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-5 h-5 text-zinc-500 animate-spin" />
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-800/50 bg-zinc-900/50">
                {['Name','Email','Role','Employee ID','Status'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-zinc-500 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {users.map((u,i) => (
                <motion.tr key={u.id}
                  initial={{ opacity:0, x:-10 }} animate={{ opacity:1, x:0 }} transition={{ delay:i*0.04 }}
                  className="border-b border-zinc-800/30 hover:bg-zinc-900/50 transition-colors"
                >
                  <td className="px-4 py-3 font-medium text-white">{u.name}</td>
                  <td className="px-4 py-3 text-zinc-400 text-xs">{u.email}</td>
                  <td className="px-4 py-3"><StatusBadge status={u.role} /></td>
                  <td className="px-4 py-3 text-zinc-400 font-mono text-xs">{u.employee_id ?? '—'}</td>
                  <td className="px-4 py-3"><StatusBadge status={u.is_active ? 'present' : 'absent'} /></td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        )}
      </motion.div>
    </div>
  )
}
