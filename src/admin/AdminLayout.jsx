import { useState, useEffect, useCallback, useMemo } from 'react'
import { Outlet, NavLink, useLocation, useOutletContext } from 'react-router-dom'
import { useAdminAuth } from './AdminAuthProvider'
import {
  Sheet,
  SheetContent,
  SheetTitle,
} from '@/components/ui/sheet'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import {
  LayoutDashboard,
  Users,
  Calendar,
  FileText,
  BarChart3,
  HelpCircle,
  Briefcase,
  Mail,
  TrendingUp,
  Activity,
  Settings,
  Sun,
  Moon,
  Globe,
  LogOut,
  Menu,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  PanelLeftClose,
  PanelLeftOpen,
  Eye,
} from 'lucide-react'

/* ================================================================== */
/*  Bilingual labels                                                   */
/* ================================================================== */
const L = {
  ar: {
    dashboard: 'لوحة التحكم',
    leads: 'العملاء المحتملون',
    bookings: 'الحجوزات',
    blog: 'المدونة',
    caseStudies: 'دراسات الحالة',
    faq: 'الأسئلة الشائعة',
    services: 'الخدمات',
    subscribers: 'المشتركون',
    trendIntelligence: 'رصد التوجهات',
    competitorIntel: 'استخبارات المنافسين',
    analytics: 'التحليلات',
    settings: 'الإعدادات',
    signOut: 'تسجيل الخروج',
    switchLang: 'English',
    lightMode: 'الوضع الفاتح',
    darkMode: 'الوضع الداكن',
    navigation: 'التنقل',
    mainSection: 'الرئيسية',
    contentSection: 'المحتوى',
    marketingSection: 'التسويق',
    systemSection: 'النظام',
    adminPanel: 'لوحة التحكم',
  },
  en: {
    dashboard: 'Dashboard',
    leads: 'Leads',
    bookings: 'Bookings',
    blog: 'Blog',
    caseStudies: 'Case Studies',
    faq: 'FAQ',
    services: 'Services',
    subscribers: 'Subscribers',
    trendIntelligence: 'Trend Intelligence',
    competitorIntel: 'Competitor Intel',
    analytics: 'Analytics',
    settings: 'Settings',
    signOut: 'Sign Out',
    switchLang: 'العربية',
    lightMode: 'Light mode',
    darkMode: 'Dark mode',
    navigation: 'Navigation',
    mainSection: 'Main',
    contentSection: 'Content',
    marketingSection: 'Marketing',
    systemSection: 'System',
    adminPanel: 'Admin Panel',
  },
}

/* ================================================================== */
/*  Nav sections with dividers                                         */
/* ================================================================== */
const NAV_SECTIONS = [
  {
    key: 'main',
    labelKey: 'mainSection',
    items: [
      { path: '/admin', icon: LayoutDashboard, labelKey: 'dashboard', end: true },
      { path: '/admin/leads', icon: Users, labelKey: 'leads' },
      { path: '/admin/bookings', icon: Calendar, labelKey: 'bookings' },
    ],
  },
  {
    key: 'content',
    labelKey: 'contentSection',
    items: [
      { path: '/admin/blog', icon: FileText, labelKey: 'blog' },
      { path: '/admin/cases', icon: BarChart3, labelKey: 'caseStudies' },
      { path: '/admin/faq', icon: HelpCircle, labelKey: 'faq' },
      { path: '/admin/services', icon: Briefcase, labelKey: 'services' },
    ],
  },
  {
    key: 'marketing',
    labelKey: 'marketingSection',
    items: [
      { path: '/admin/subscribers', icon: Mail, labelKey: 'subscribers' },
      { path: '/admin/trends', icon: TrendingUp, labelKey: 'trendIntelligence' },
      { path: '/admin/competitor', icon: Eye, labelKey: 'competitorIntel' },
    ],
  },
  {
    key: 'system',
    labelKey: 'systemSection',
    items: [
      { path: '/admin/analytics', icon: Activity, labelKey: 'analytics' },
      { path: '/admin/settings', icon: Settings, labelKey: 'settings' },
    ],
  },
]

/* ================================================================== */
/*  SidebarContent (shared between desktop + mobile)                   */
/* ================================================================== */
function SidebarContent({ collapsed, onToggle, lang, isDark, profile, user }) {
  const t = L[lang] || L.en
  const isRTL = lang === 'ar'

  const userDisplayName =
    profile?.display_name || user?.email?.split('@')[0] || 'Admin'
  const userInitial = userDisplayName.charAt(0).toUpperCase()

  return (
    <div
      className={`h-full flex flex-col transition-colors duration-200 ${
        isDark
          ? 'bg-slate-900 border-slate-800'
          : 'bg-white border-gray-200'
      }`}
    >
      {/* ---- Header: Ziyada wordmark + collapse toggle ---- */}
      <div
        className={`flex items-center h-14 px-3 border-b flex-shrink-0 ${
          isDark ? 'border-slate-800' : 'border-gray-200'
        }`}
      >
        {!collapsed && (
          <span className="text-lg font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent truncate flex-1">
            Ziyada
          </span>
        )}
        {collapsed && (
          <span className="text-lg font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent mx-auto">
            Z
          </span>
        )}
        <button
          onClick={onToggle}
          className={`p-1.5 rounded-md transition-colors hidden lg:flex items-center justify-center ${
            isDark
              ? 'hover:bg-slate-800 text-slate-400'
              : 'hover:bg-gray-100 text-gray-500'
          } ${collapsed ? 'mx-auto' : ''}`}
          title={collapsed ? 'Expand' : 'Collapse'}
        >
          {collapsed ? (
            <PanelLeftOpen className="w-4 h-4" />
          ) : (
            <PanelLeftClose className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* ---- Navigation ---- */}
      <ScrollArea className="flex-1">
        <nav className="py-2 px-2">
          {NAV_SECTIONS.map((section, sIdx) => (
            <div key={section.key}>
              {/* Section divider (not before the first section) */}
              {sIdx > 0 && (
                <div
                  className={`mx-3 my-2 h-px ${
                    isDark ? 'bg-slate-800' : 'bg-gray-200'
                  }`}
                />
              )}

              {/* Section label (hidden when collapsed) */}
              {!collapsed && (
                <p
                  className={`px-3 pt-2 pb-1 text-[10px] font-semibold uppercase tracking-wider ${
                    isDark ? 'text-slate-500' : 'text-gray-400'
                  }`}
                >
                  {t[section.labelKey]}
                </p>
              )}

              {/* Nav items */}
              <div className="space-y-0.5">
                {section.items.map((item) => {
                  const Icon = item.icon
                  const label = t[item.labelKey]

                  const linkContent = (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      end={item.end}
                      className={({ isActive }) =>
                        `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors relative ${
                          isActive
                            ? isDark
                              ? 'bg-blue-600/15 text-blue-400'
                              : 'bg-blue-50 text-blue-600'
                            : isDark
                            ? 'text-slate-400 hover:text-white hover:bg-slate-800'
                            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                        } ${collapsed ? 'justify-center px-2' : ''}`
                      }
                    >
                      {({ isActive }) => (
                        <>
                          <Icon className="w-5 h-5 flex-shrink-0" />
                          {!collapsed && (
                            <span className="truncate">{label}</span>
                          )}
                          {/* Active bar */}
                          {isActive && (
                            <span
                              className={`absolute top-1/2 -translate-y-1/2 w-1 h-5 rounded-full bg-blue-500 ${
                                isRTL ? 'right-0 -mr-2' : 'left-0 -ml-2'
                              }`}
                            />
                          )}
                        </>
                      )}
                    </NavLink>
                  )

                  /* wrap collapsed items in tooltip */
                  if (collapsed) {
                    return (
                      <Tooltip key={item.path} delayDuration={0}>
                        <TooltipTrigger asChild>{linkContent}</TooltipTrigger>
                        <TooltipContent
                          side={isRTL ? 'left' : 'right'}
                          className={
                            isDark
                              ? 'bg-slate-700 text-white border-slate-600'
                              : 'bg-gray-800 text-white border-gray-700'
                          }
                        >
                          {label}
                        </TooltipContent>
                      </Tooltip>
                    )
                  }

                  return <div key={item.path}>{linkContent}</div>
                })}
              </div>
            </div>
          ))}
        </nav>
      </ScrollArea>

      {/* ---- Bottom: user avatar + name ---- */}
      <div
        className={`flex-shrink-0 border-t p-3 ${
          isDark ? 'border-slate-800' : 'border-gray-200'
        }`}
      >
        <div
          className={`flex items-center gap-3 rounded-lg px-2 py-2 ${
            collapsed ? 'justify-center' : ''
          }`}
        >
          {/* Avatar circle */}
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0 shadow-sm">
            {userInitial}
          </div>
          {!collapsed && (
            <div className="min-w-0 flex-1">
              <p
                className={`text-sm font-medium truncate ${
                  isDark ? 'text-slate-200' : 'text-gray-800'
                }`}
              >
                {userDisplayName}
              </p>
              <p
                className={`text-xs truncate ${
                  isDark ? 'text-slate-500' : 'text-gray-400'
                }`}
              >
                {profile?.role || 'admin'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

/* ================================================================== */
/*  Topbar                                                             */
/* ================================================================== */
function Topbar({ lang, toggleLang, isDark, toggleTheme, user, profile, onSignOut, onMobileMenu }) {
  const location = useLocation()
  const t = L[lang] || L.en
  const isRTL = lang === 'ar'

  const [menuOpen, setMenuOpen] = useState(false)

  /* derive page title from pathname */
  const pageTitle = useMemo(() => {
    const allItems = NAV_SECTIONS.flatMap((s) => s.items)
    const matched =
      allItems.find((i) => i.end && location.pathname === i.path) ||
      allItems.find(
        (i) => !i.end && location.pathname.startsWith(i.path) && i.path !== '/admin'
      ) ||
      allItems[0]
    return t[matched.labelKey]
  }, [location.pathname, t])

  /* close dropdown on outside click */
  useEffect(() => {
    if (!menuOpen) return
    const handler = (e) => {
      if (!e.target.closest('[data-user-menu]')) setMenuOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [menuOpen])

  const userDisplayName =
    profile?.display_name || user?.email?.split('@')[0] || 'Admin'
  const userInitial = userDisplayName.charAt(0).toUpperCase()

  return (
    <header
      className={`h-14 flex items-center justify-between px-4 border-b flex-shrink-0 ${
        isDark
          ? 'bg-slate-900/80 backdrop-blur-sm border-slate-800'
          : 'bg-white/80 backdrop-blur-sm border-gray-200'
      }`}
    >
      {/* Left: hamburger + page title */}
      <div className="flex items-center gap-3 min-w-0">
        <button
          onClick={onMobileMenu}
          className={`p-1.5 rounded-md lg:hidden transition-colors ${
            isDark ? 'hover:bg-slate-800 text-slate-400' : 'hover:bg-gray-100 text-gray-500'
          }`}
        >
          <Menu className="w-5 h-5" />
        </button>
        <h2
          className={`text-base font-semibold truncate ${
            isDark ? 'text-white' : 'text-gray-900'
          }`}
        >
          {pageTitle}
        </h2>
      </div>

      {/* Right: lang, theme, user */}
      <div className="flex items-center gap-1.5">
        {/* Language toggle */}
        <button
          onClick={toggleLang}
          className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors ${
            isDark
              ? 'hover:bg-slate-800 text-slate-400 hover:text-white'
              : 'hover:bg-gray-100 text-gray-500 hover:text-gray-900'
          }`}
          title={lang === 'ar' ? 'Switch to English' : 'التبديل إلى العربية'}
        >
          <Globe className="w-4 h-4" />
          <span>{lang === 'ar' ? 'EN' : 'AR'}</span>
        </button>

        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className={`p-1.5 rounded-md transition-colors ${
            isDark
              ? 'hover:bg-slate-800 text-slate-400 hover:text-white'
              : 'hover:bg-gray-100 text-gray-500 hover:text-gray-900'
          }`}
          title={isDark ? t.lightMode : t.darkMode}
        >
          {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* User menu */}
        <div className="relative" data-user-menu>
          <button
            onClick={() => setMenuOpen((v) => !v)}
            className={`flex items-center gap-2 px-2 py-1 rounded-md transition-colors ${
              isDark
                ? 'hover:bg-slate-800 text-slate-300'
                : 'hover:bg-gray-100 text-gray-700'
            }`}
          >
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold">
              {userInitial}
            </div>
            <ChevronDown
              className={`w-3.5 h-3.5 transition-transform ${menuOpen ? 'rotate-180' : ''}`}
            />
          </button>

          {/* Dropdown */}
          {menuOpen && (
            <div
              className={`absolute top-full mt-1.5 w-52 rounded-xl shadow-xl border z-50 overflow-hidden ${
                isRTL ? 'left-0' : 'right-0'
              } ${
                isDark
                  ? 'bg-slate-800 border-slate-700'
                  : 'bg-white border-gray-200'
              }`}
            >
              {/* User info */}
              <div
                className={`px-3 py-2.5 border-b ${
                  isDark ? 'border-slate-700' : 'border-gray-100'
                }`}
              >
                <p
                  className={`text-sm font-medium truncate ${
                    isDark ? 'text-slate-200' : 'text-gray-800'
                  }`}
                >
                  {userDisplayName}
                </p>
                <p
                  className={`text-xs truncate ${
                    isDark ? 'text-slate-500' : 'text-gray-400'
                  }`}
                >
                  {user?.email || ''}
                </p>
              </div>

              {/* Sign out */}
              <button
                onClick={() => {
                  setMenuOpen(false)
                  onSignOut()
                }}
                className={`w-full flex items-center gap-2 px-3 py-2.5 text-sm transition-colors ${
                  isDark
                    ? 'text-red-400 hover:bg-slate-700/60'
                    : 'text-red-600 hover:bg-red-50'
                }`}
              >
                <LogOut className="w-4 h-4" />
                <span>{t.signOut}</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

/* ================================================================== */
/*  AdminLayout (main export)                                          */
/* ================================================================== */
export default function AdminLayout() {
  const { user, profile, signOut } = useAdminAuth()
  const location = useLocation()

  /* ---- Theme (dark by default, independent of public site) ---- */
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem('ziyada_admin_theme') || 'dark'
    } catch {
      return 'dark'
    }
  })

  /* ---- Language ---- */
  const [lang, setLang] = useState(() => {
    try {
      return localStorage.getItem('ziyada_lang') || 'ar'
    } catch {
      return 'ar'
    }
  })

  /* ---- Sidebar collapse (desktop) ---- */
  const [collapsed, setCollapsed] = useState(false)

  /* ---- Mobile sheet open ---- */
  const [mobileOpen, setMobileOpen] = useState(false)

  /* persist theme */
  useEffect(() => {
    try {
      localStorage.setItem('ziyada_admin_theme', theme)
    } catch {
      /* noop */
    }
  }, [theme])

  /* persist lang */
  useEffect(() => {
    try {
      localStorage.setItem('ziyada_lang', lang)
    } catch {
      /* noop */
    }
  }, [lang])

  /* close mobile sheet on navigate */
  useEffect(() => {
    setMobileOpen(false)
  }, [location.pathname])

  /* handlers */
  const toggleTheme = useCallback(
    () => setTheme((p) => (p === 'dark' ? 'light' : 'dark')),
    []
  )
  const toggleLang = useCallback(
    () => setLang((p) => (p === 'ar' ? 'en' : 'ar')),
    []
  )
  const toggleCollapsed = useCallback(() => setCollapsed((p) => !p), [])
  const handleSignOut = useCallback(async () => {
    await signOut()
  }, [signOut])

  const isDark = theme === 'dark'
  const isRTL = lang === 'ar'

  return (
    <TooltipProvider>
      <div
        className={`min-h-screen flex ${
          isDark ? 'bg-slate-950 text-white' : 'bg-gray-50 text-gray-900'
        }`}
        dir={isRTL ? 'rtl' : 'ltr'}
        style={{
          fontFamily: isRTL
            ? "'Noto Kufi Arabic', sans-serif"
            : "'Plus Jakarta Sans', sans-serif",
        }}
      >
        {/* ============ Desktop sidebar ============ */}
        <aside
          className={`hidden lg:flex flex-shrink-0 transition-all duration-300 ease-in-out border-e ${
            isDark ? 'border-slate-800' : 'border-gray-200'
          } ${collapsed ? 'w-[4.5rem]' : 'w-60'}`}
        >
          <div className="w-full">
            <SidebarContent
              collapsed={collapsed}
              onToggle={toggleCollapsed}
              lang={lang}
              isDark={isDark}
              profile={profile}
              user={user}
            />
          </div>
        </aside>

        {/* ============ Mobile sidebar (Sheet) ============ */}
        <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
          <SheetContent
            side={isRTL ? 'right' : 'left'}
            className={`p-0 w-64 ${
              isDark
                ? 'bg-slate-900 border-slate-800'
                : 'bg-white border-gray-200'
            }`}
          >
            <SheetTitle className="sr-only">
              {L[lang]?.navigation || 'Navigation'}
            </SheetTitle>
            <SidebarContent
              collapsed={false}
              onToggle={() => setMobileOpen(false)}
              lang={lang}
              isDark={isDark}
              profile={profile}
              user={user}
            />
          </SheetContent>
        </Sheet>

        {/* ============ Main column ============ */}
        <div className="flex-1 flex flex-col min-w-0">
          <Topbar
            lang={lang}
            toggleLang={toggleLang}
            isDark={isDark}
            toggleTheme={toggleTheme}
            user={user}
            profile={profile}
            onSignOut={handleSignOut}
            onMobileMenu={() => setMobileOpen(true)}
          />

          {/* Page content */}
          <main className="flex-1 p-4 md:p-6 overflow-auto">
            <Outlet context={{ theme, lang, isRTL, isDark }} />
          </main>
        </div>
      </div>
    </TooltipProvider>
  )
}

/**
 * Hook for child routes to access layout context.
 * Usage: const { lang, isRTL, theme, isDark } = useAdminLayoutContext()
 */
export function useAdminLayoutContext() {
  return useOutletContext()
}
