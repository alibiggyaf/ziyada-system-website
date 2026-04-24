import { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Menu,
  Sun,
  Moon,
  Globe,
  LogOut,
  ChevronDown,
} from 'lucide-react';

const PAGE_TITLES = {
  ar: {
    '/admin': 'لوحة التحكم',
    '/admin/leads': 'العملاء المحتملين',
    '/admin/bookings': 'الحجوزات',
    '/admin/blog': 'المدونة',
    '/admin/cases': 'دراسات الحالة',
    '/admin/faq': 'الأسئلة الشائعة',
    '/admin/services': 'الخدمات',
    '/admin/subscribers': 'المشتركين',
    '/admin/trends': 'التوجهات',
    '/admin/analytics': 'التحليلات',
    '/admin/settings': 'الإعدادات',
  },
  en: {
    '/admin': 'Dashboard',
    '/admin/leads': 'Leads',
    '/admin/bookings': 'Bookings',
    '/admin/blog': 'Blog',
    '/admin/cases': 'Case Studies',
    '/admin/faq': 'FAQ',
    '/admin/services': 'Services',
    '/admin/subscribers': 'Subscribers',
    '/admin/trends': 'Trends',
    '/admin/analytics': 'Analytics',
    '/admin/settings': 'Settings',
  },
};

export default function AdminTopbar({
  lang,
  toggleLang,
  theme,
  toggleTheme,
  user,
  onSignOut,
  onToggleSidebar,
}) {
  const location = useLocation();
  const isDark = theme === 'dark';
  const isRTL = lang === 'ar';
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const menuRef = useRef(null);

  // Derive page title from location
  const titles = PAGE_TITLES[lang] || PAGE_TITLES.en;
  const pageTitle =
    titles[location.pathname] ||
    titles[
      Object.keys(titles).find(
        (key) => key !== '/admin' && location.pathname.startsWith(key)
      )
    ] ||
    titles['/admin'];

  // Close menu on outside click
  useEffect(() => {
    const handler = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setUserMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const userInitial = user?.email
    ? user.email.charAt(0).toUpperCase()
    : 'A';

  return (
    <header
      className={`h-14 flex items-center justify-between px-4 border-b flex-shrink-0 ${
        isDark
          ? 'bg-slate-900/60 border-slate-700/50'
          : 'bg-white border-gray-200'
      }`}
    >
      {/* Left side */}
      <div className="flex items-center gap-3">
        {/* Mobile hamburger */}
        <button
          onClick={onToggleSidebar}
          className={`p-1.5 rounded-md lg:hidden transition-colors ${
            isDark ? 'hover:bg-slate-700 text-slate-400' : 'hover:bg-gray-100 text-gray-500'
          }`}
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Page title */}
        <h2
          className={`text-base font-semibold ${
            isDark ? 'text-white' : 'text-gray-900'
          }`}
        >
          {pageTitle}
        </h2>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-2">
        {/* Language toggle */}
        <button
          onClick={toggleLang}
          className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors ${
            isDark
              ? 'hover:bg-slate-700 text-slate-400 hover:text-white'
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
              ? 'hover:bg-slate-700 text-slate-400 hover:text-white'
              : 'hover:bg-gray-100 text-gray-500 hover:text-gray-900'
          }`}
          title={isDark ? 'Light mode' : 'Dark mode'}
        >
          {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* User menu */}
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setUserMenuOpen(!userMenuOpen)}
            className={`flex items-center gap-2 px-2 py-1 rounded-md transition-colors ${
              isDark
                ? 'hover:bg-slate-700 text-slate-300'
                : 'hover:bg-gray-100 text-gray-700'
            }`}
          >
            {/* Avatar */}
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-bold">
              {userInitial}
            </div>
            <ChevronDown className="w-3.5 h-3.5" />
          </button>

          {/* Dropdown */}
          {userMenuOpen && (
            <div
              className={`absolute top-full mt-1 w-48 rounded-lg shadow-xl border z-50 overflow-hidden ${
                isRTL ? 'left-0' : 'right-0'
              } ${
                isDark
                  ? 'bg-slate-800 border-slate-700'
                  : 'bg-white border-gray-200'
              }`}
            >
              {/* User info */}
              <div
                className={`px-3 py-2 border-b text-xs truncate ${
                  isDark
                    ? 'border-slate-700 text-slate-400'
                    : 'border-gray-100 text-gray-500'
                }`}
              >
                {user?.email || 'admin@ziyada.sa'}
              </div>

              {/* Sign out */}
              <button
                onClick={() => {
                  setUserMenuOpen(false);
                  onSignOut();
                }}
                className={`w-full flex items-center gap-2 px-3 py-2 text-sm transition-colors ${
                  isDark
                    ? 'text-red-400 hover:bg-slate-700'
                    : 'text-red-600 hover:bg-red-50'
                }`}
              >
                <LogOut className="w-4 h-4" />
                <span>{lang === 'ar' ? 'تسجيل الخروج' : 'Sign Out'}</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
