import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAdminAuth } from './AdminAuthProvider'
import { Loader2, Eye, EyeOff, Lock } from 'lucide-react'

/* ------------------------------------------------------------------ */
/*  Bilingual text                                                     */
/* ------------------------------------------------------------------ */
const L = {
  ar: {
    brand: 'Ziyada',
    subtitle: 'لوحة التحكم',
    email: 'البريد الإلكتروني',
    password: 'كلمة المرور',
    signIn: 'تسجيل الدخول',
    emailPlaceholder: 'أدخل بريدك الإلكتروني',
    passwordPlaceholder: 'أدخل كلمة المرور',
    errorInvalid: 'البريد الإلكتروني أو كلمة المرور غير صحيحة',
    errorGeneric: 'حدث خطأ أثناء تسجيل الدخول',
    copyright: 'Ziyada Systems',
  },
  en: {
    brand: 'Ziyada',
    subtitle: 'Admin Panel',
    email: 'Email',
    password: 'Password',
    signIn: 'Sign In',
    emailPlaceholder: 'Enter your email',
    passwordPlaceholder: 'Enter your password',
    errorInvalid: 'Invalid email or password',
    errorGeneric: 'An error occurred during sign in',
    copyright: 'Ziyada Systems',
  },
}

/* ------------------------------------------------------------------ */
/*  AdminLogin                                                         */
/* ------------------------------------------------------------------ */
export default function AdminLogin() {
  const { signIn, session } = useAdminAuth()
  const navigate = useNavigate()

  const [lang] = useState(() => {
    try {
      return localStorage.getItem('ziyada_lang') || 'ar'
    } catch {
      return 'ar'
    }
  })

  const t = L[lang] || L.ar
  const isRTL = lang === 'ar'

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  /* redirect if already signed in */
  useEffect(() => {
    if (session) {
      navigate('/admin', { replace: true })
    }
  }, [session, navigate])

  /* form submit */
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)

    try {
      await signIn(email, password)
      navigate('/admin', { replace: true })
    } catch (err) {
      if (err?.message?.toLowerCase().includes('invalid')) {
        setError(t.errorInvalid)
      } else {
        setError(t.errorGeneric)
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center bg-slate-950 px-4"
      dir={isRTL ? 'rtl' : 'ltr'}
      style={{ fontFamily: isRTL ? "'Noto Kufi Arabic', sans-serif" : "'Plus Jakarta Sans', sans-serif" }}
    >
      {/* Background gradient */}
      <div className="fixed inset-0 bg-gradient-to-br from-blue-950/40 via-slate-950 to-purple-950/30 pointer-events-none" />

      {/* Subtle grid pattern */}
      <div
        className="fixed inset-0 opacity-[0.03] pointer-events-none"
        style={{
          backgroundImage:
            'linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px)',
          backgroundSize: '40px 40px',
        }}
      />

      <div className="relative w-full max-w-md z-10">
        {/* Gradient border wrapper */}
        <div className="rounded-2xl p-px bg-gradient-to-br from-blue-500 via-purple-500/50 to-blue-500/30">
          {/* Card */}
          <div className="rounded-2xl bg-slate-900/90 backdrop-blur-xl p-8">
            {/* Lock icon badge */}
            <div className="flex justify-center mb-6">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
                <Lock className="w-6 h-6 text-white" />
              </div>
            </div>

            {/* Brand + subtitle */}
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-white tracking-tight">
                {t.brand}
              </h1>
              <p className="text-slate-400 mt-1.5 text-sm font-medium">
                {t.subtitle}
              </p>
            </div>

            {/* Error message */}
            {error && (
              <div className="mb-5 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm text-center">
                {error}
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">
                  {t.email}
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={t.emailPlaceholder}
                  className="w-full px-4 py-2.5 bg-slate-800/60 border border-slate-700/50 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/40 transition-all"
                  autoComplete="email"
                  dir="ltr"
                />
              </div>

              {/* Password */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">
                  {t.password}
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder={t.passwordPlaceholder}
                    className="w-full px-4 py-2.5 bg-slate-800/60 border border-slate-700/50 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/40 transition-all"
                    autoComplete="current-password"
                    dir="ltr"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className={`absolute top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300 transition-colors ${
                      isRTL ? 'left-3' : 'right-3'
                    }`}
                    tabIndex={-1}
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={submitting}
                className="w-full py-2.5 rounded-lg font-semibold text-white transition-all flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/20 hover:shadow-blue-500/30"
              >
                {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
                {t.signIn}
              </button>

              {/* Forgot password link */}
              <div className="text-center mt-3">
                <a
                  href="/admin/reset-password"
                  className="text-blue-400 hover:underline text-sm"
                >
                  {isRTL ? 'نسيت كلمة المرور؟' : 'Forgot password?'}
                </a>
              </div>
            </form>
          </div>
        </div>

        {/* Bottom branding */}
        <p className="text-center text-slate-600 text-xs mt-6">
          {t.copyright} &copy; {new Date().getFullYear()}
        </p>
      </div>
    </div>
  )
}
