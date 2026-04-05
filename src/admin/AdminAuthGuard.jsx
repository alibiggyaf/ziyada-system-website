import { Navigate, Outlet } from 'react-router-dom'
import { useAdminAuth } from './AdminAuthProvider'
import { Loader2 } from 'lucide-react'

/**
 * Wraps admin routes.
 *  - loading  -> spinner
 *  - no session -> redirect to /admin/login
 *  - session exists -> render children (or <Outlet /> when used as a layout route)
 */
export default function AdminAuthGuard({ children }) {
  const { session, loading } = useAdminAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
          <p className="text-sm text-slate-500 font-medium">Loading&hellip;</p>
        </div>
      </div>
    )
  }

  if (!session) {
    return <Navigate to="/admin/login" replace />
  }

  return children ?? <Outlet />
}
