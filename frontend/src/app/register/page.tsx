'use client'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { Scan, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'
import { authApi } from '@/services/api'

export default function RegisterPage() {
  const router = useRouter()
  const [form, setForm] = useState({
    name: '', email: '', password: '', role: 'admin', employee_id: ''
  })
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(''); setLoading(true)
    try {
      await authApi.register({
        name:        form.name,
        email:       form.email,
        password:    form.password,
        role:        form.role,
        employee_id: form.role === 'user' ? form.employee_id : undefined,
      })
      setSuccess(true)
      setTimeout(() => router.push('/login'), 1500)
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      setError(err?.response?.data?.detail ?? 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="flex items-center gap-2 mb-8">
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
            <Scan className="w-4 h-4 text-blue-400" />
          </div>
          <span className="font-bold text-white">FaceAttend</span>
        </div>

        <div className="mb-6">
          <h2 className="text-2xl font-bold text-white">Create Account</h2>
          <p className="text-zinc-500 text-sm mt-1">Register as admin or user</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1.5">Full Name</label>
            <input type="text" value={form.name} onChange={e => setForm(p=>({...p,name:e.target.value}))}
              placeholder="John Doe" required
              className="w-full px-4 py-3 rounded-xl bg-zinc-900 border border-zinc-800 text-white text-sm placeholder-zinc-600 focus:outline-none focus:border-blue-500/50 transition-all"
            />
          </div>

          {/* Email */}
          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1.5">Email</label>
            <input type="email" value={form.email} onChange={e => setForm(p=>({...p,email:e.target.value}))}
              placeholder="you@example.com" required
              className="w-full px-4 py-3 rounded-xl bg-zinc-900 border border-zinc-800 text-white text-sm placeholder-zinc-600 focus:outline-none focus:border-blue-500/50 transition-all"
            />
          </div>

          {/* Password */}
          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1.5">Password</label>
            <input type="password" value={form.password} onChange={e => setForm(p=>({...p,password:e.target.value}))}
              placeholder="••••••••" required
              className="w-full px-4 py-3 rounded-xl bg-zinc-900 border border-zinc-800 text-white text-sm placeholder-zinc-600 focus:outline-none focus:border-blue-500/50 transition-all"
            />
          </div>

          {/* Role */}
          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1.5">Role</label>
            <div className="grid grid-cols-2 gap-3">
              {['admin','user'].map(r => (
                <motion.button
                  key={r} type="button"
                  whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
                  onClick={() => setForm(p=>({...p,role:r}))}
                  className={`py-3 rounded-xl border text-sm font-medium capitalize transition-all ${
                    form.role === r
                      ? r === 'admin'
                        ? 'bg-purple-500/10 border-purple-500/40 text-purple-400'
                        : 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400'
                      : 'bg-zinc-900 border-zinc-800 text-zinc-500 hover:border-zinc-600'
                  }`}
                >
                  {r}
                </motion.button>
              ))}
            </div>
          </div>

          {/* Employee ID — only for user role */}
          <AnimatePresence>
            {form.role === 'user' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <label className="block text-xs font-medium text-zinc-400 mb-1.5">Employee ID</label>
                <input type="text" value={form.employee_id} onChange={e => setForm(p=>({...p,employee_id:e.target.value}))}
                  placeholder="EMP001" required={form.role==='user'}
                  className="w-full px-4 py-3 rounded-xl bg-zinc-900 border border-zinc-800 text-white text-sm placeholder-zinc-600 focus:outline-none focus:border-emerald-500/50 transition-all"
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Error */}
          <AnimatePresence>
            {error && (
              <motion.div initial={{ opacity:0, y:-5 }} animate={{ opacity:1, y:0 }} exit={{ opacity:0 }}
                className="flex items-center gap-2 p-3 rounded-xl bg-red-500/5 border border-red-500/20"
              >
                <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
                <p className="text-sm text-red-400">{error}</p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Success */}
          <AnimatePresence>
            {success && (
              <motion.div initial={{ opacity:0, y:-5 }} animate={{ opacity:1, y:0 }}
                className="flex items-center gap-2 p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/20"
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <p className="text-sm text-emerald-400">Account created! Redirecting to login...</p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Submit */}
          <motion.button whileHover={{ scale:1.01 }} whileTap={{ scale:0.98 }}
            type="submit" disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold transition-colors disabled:opacity-60"
          >
            {loading ? <><Loader2 className="w-4 h-4 animate-spin" />Creating...</> : 'Create Account'}
          </motion.button>

          {/* Link to login */}
          <p className="text-center text-xs text-zinc-500">
            Already have an account?{' '}
            <a href="/login" className="text-blue-400 hover:text-blue-300 transition-colors">Sign in</a>
          </p>
        </form>
      </motion.div>
    </div>
  )
}