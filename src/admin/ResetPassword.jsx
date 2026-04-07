import { useState } from 'react'
import { requestPasswordReset } from '../api/resetPassword'

const L = {
  ar: {
    title: 'إعادة تعيين كلمة المرور',
    email: 'البريد الإلكتروني',
    emailPlaceholder: 'أدخل بريدك الإلكتروني',
    submit: 'إرسال رابط إعادة التعيين',
    success: 'تم إرسال رابط إعادة التعيين إلى بريدك الإلكتروني (إذا كان موجودًا لدينا).',
    error: 'حدث خطأ أثناء إرسال الرابط. حاول مرة أخرى.',
    back: 'العودة لتسجيل الدخول',
  },
  en: {
    title: 'Reset Password',
    email: 'Email',
    emailPlaceholder: 'Enter your email',
    submit: 'Send Reset Link',
    success: 'A reset link has been sent to your email (if it exists in our system).',
    error: 'An error occurred while sending the link. Please try again.',
    back: 'Back to Login',
  },
}

export default function ResetPassword() {
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
  const [status, setStatus] = useState('idle') // idle | success | error

  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatus('idle')
    const { success } = await requestPasswordReset(email)
    setStatus(success ? 'success' : 'error')
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center bg-slate-950 px-4"
      dir={isRTL ? 'rtl' : 'ltr'}
      style={{ fontFamily: isRTL ? "'Noto Kufi Arabic', sans-serif" : "'Plus Jakarta Sans', sans-serif" }}
    >
      <div className="relative w-full max-w-md z-10">
        <div className="rounded-2xl p-px bg-gradient-to-br from-blue-500 via-purple-500/50 to-blue-500/30">
          <div className="rounded-2xl bg-slate-900/90 backdrop-blur-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6 text-center">{t.title}</h2>
            {status === 'success' ? (
              <div className="mb-5 p-3 bg-green-500/10 border border-green-500/30 rounded-lg text-green-400 text-sm text-center">
                {t.success}
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-5">
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
                <button
                  type="submit"
                  className="w-full py-2.5 rounded-lg font-semibold text-white transition-all flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 shadow-lg shadow-blue-500/20 hover:shadow-blue-500/30"
                >
                  {t.submit}
                </button>
                {status === 'error' && (
                  <div className="mt-3 p-2 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-xs text-center">
                    {t.error}
                  </div>
                )}
              </form>
            )}
            <div className="text-center mt-6">
              <a href="/admin/login" className="text-blue-400 hover:underline text-sm">{t.back}</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
