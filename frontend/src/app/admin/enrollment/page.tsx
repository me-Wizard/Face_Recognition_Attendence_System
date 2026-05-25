'use client'
// src/app/admin/enrollment/page.tsx

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { UserPlus, Trash2, CheckCircle2, XCircle } from 'lucide-react'
import { GlowButton } from '@/components/shared'
import { enrollApi } from '@/services/api'

export default function EnrollmentPage() {
  const [form,    setForm]    = useState({ name: '', employee_id: '', department: '' })
  const [loading, setLoading] = useState(false)
  const [result,  setResult]  = useState<{ ok: boolean; msg: string } | null>(null)
  const [delId,   setDelId]   = useState('')

  const enroll = async () => {
    if (!form.name || !form.employee_id || !form.department) return
    setLoading(true); setResult(null)
    try {
      await enrollApi.startEnrollment(form)
      setResult({ ok: true, msg: `${form.name} enrolled. Camera will open on server.` })
      setForm({ name: '', employee_id: '', department: '' })
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      setResult({ ok: false, msg: err?.response?.data?.detail ?? 'Enrollment failed' })
    } finally { setLoading(false) }
  }

  const remove = async () => {
    if (!delId) return
    setLoading(true); setResult(null)
    try {
      await enrollApi.deleteUser(delId)
      setResult({ ok: true, msg: `${delId} removed successfully.` })
      setDelId('')
    } catch {
      setResult({ ok: false, msg: 'User not found' })
    } finally { setLoading(false) }
  }

  return (
    <div className="max-w-xl mx-auto space-y-5">
      {/* Enroll */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-6"
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
            <UserPlus className="w-4 h-4 text-blue-400" />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">Enroll New Person</p>
            <p className="text-xs text-zinc-500">Camera opens on server to capture face samples</p>
          </div>
        </div>

        <div className="space-y-4">
          {[
            { k: 'name',        label: 'Full Name',   ph: 'John Doe'    },
            { k: 'employee_id', label: 'Employee ID', ph: 'EMP-001'     },
            { k: 'department',  label: 'Department',  ph: 'Engineering' },
          ].map((f, i) => (
            <motion.div key={f.k} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.07 }}>
              <label className="block text-xs font-medium text-zinc-400 mb-1.5">{f.label}</label>
              <input
                type="text"
                value={form[f.k as keyof typeof form]}
                onChange={e => setForm(p => ({ ...p, [f.k]: e.target.value }))}
                placeholder={f.ph}
                className="w-full px-3 py-2.5 rounded-lg bg-zinc-800/50 border border-zinc-700/50 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all"
              />
            </motion.div>
          ))}
        </div>

        <GlowButton onClick={enroll} loading={loading} className="w-full justify-center mt-5">
          <UserPlus className="w-4 h-4" /> Start Enrollment
        </GlowButton>
      </motion.div>

      {/* Result */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className={`flex items-center gap-3 p-4 rounded-xl border ${
              result.ok
                ? 'bg-emerald-500/5 border-emerald-500/20'
                : 'bg-red-500/5 border-red-500/20'
            }`}
          >
            {result.ok
              ? <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              : <XCircle     className="w-4 h-4 text-red-400 shrink-0" />
            }
            <p className={`text-sm ${result.ok ? 'text-emerald-400' : 'text-red-400'}`}>{result.msg}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Delete */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
        className="rounded-xl bg-zinc-900 border border-zinc-800/50 p-5"
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center">
            <Trash2 className="w-4 h-4 text-red-400" />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">Remove Person</p>
            <p className="text-xs text-zinc-500">Deletes user and all face embeddings</p>
          </div>
        </div>
        <div className="flex gap-3">
          <input
            type="text" value={delId} onChange={e => setDelId(e.target.value)}
            placeholder="Employee ID to remove"
            className="flex-1 px-3 py-2.5 rounded-lg bg-zinc-800/50 border border-zinc-700/50 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-red-500/30 transition-all"
          />
          <GlowButton variant="danger" onClick={remove} loading={loading}>Remove</GlowButton>
        </div>
      </motion.div>
    </div>
  )
}
