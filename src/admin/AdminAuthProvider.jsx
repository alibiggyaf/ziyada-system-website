import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { supabase } from '@/lib/supabase'

const AdminAuthContext = createContext(null)

export function useAdminAuth() {
  const ctx = useContext(AdminAuthContext)
  if (!ctx) {
    throw new Error('useAdminAuth must be used within <AdminAuthProvider>')
  }
  return ctx
}

export function AdminAuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [session, setSession] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  /* ---- fetch role + display_name from the profiles table ---- */
  const fetchProfile = useCallback(async (userId) => {
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('id, role, display_name, avatar_url, email')
        .eq('id', userId)
        .single()

      if (error) {
        console.warn('[AdminAuth] Profile fetch failed:', error.message)
        setProfile(null)
      } else {
        setProfile(data)
      }
    } catch (err) {
      console.error('[AdminAuth] Profile fetch error:', err)
      setProfile(null)
    }
  }, [])

  /* ---- subscribe to auth state changes on mount ---- */
  useEffect(() => {
    // 1. Get the initial session
    supabase.auth.getSession().then(({ data: { session: initial } }) => {
      setSession(initial)
      setUser(initial?.user ?? null)

      if (initial?.user) {
        fetchProfile(initial.user.id).finally(() => setLoading(false))
      } else {
        setLoading(false)
      }
    })

    // 2. Listen for sign-in / sign-out / token refresh
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, newSession) => {
      setSession(newSession)
      setUser(newSession?.user ?? null)

      if (newSession?.user) {
        await fetchProfile(newSession.user.id)
      } else {
        setProfile(null)
      }
      setLoading(false)
    })

    return () => subscription.unsubscribe()
  }, [fetchProfile])

  /* ---- actions ---- */
  const signIn = useCallback(async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    if (error) throw error
    return data
  }, [])

  const signOut = useCallback(async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
    setUser(null)
    setSession(null)
    setProfile(null)
  }, [])

  /* ---- provider ---- */
  const value = {
    user,
    session,
    profile,
    loading,
    signIn,
    signOut,
  }

  return (
    <AdminAuthContext.Provider value={value}>
      {children}
    </AdminAuthContext.Provider>
  )
}

export { AdminAuthContext }
export default AdminAuthProvider
