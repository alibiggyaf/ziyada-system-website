import { NavLink } from 'react-router-dom';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function AdminSidebar({
  items,
  activePath,
  collapsed,
  onToggle,
  lang,
  theme,
}) {
  const isRTL = lang === 'ar';
  const isDark = theme === 'dark';

  const isActive = (item) => {
    if (item.exact) {
      return activePath === item.path;
    }
    return activePath.startsWith(item.path);
  };

  return (
    <div
      className={`h-screen flex flex-col border-e transition-all duration-300 ease-in-out ${
        isDark
          ? 'bg-slate-900/80 border-slate-700/50'
          : 'bg-white border-gray-200'
      } ${collapsed ? 'w-16' : 'w-60'}`}
    >
      {/* Header */}
      <div
        className={`flex items-center h-14 px-3 border-b ${
          isDark ? 'border-slate-700/50' : 'border-gray-200'
        }`}
      >
        {!collapsed && (
          <span className="text-lg font-bold text-blue-500 truncate flex-1">
            Ziyada
          </span>
        )}
        {collapsed && (
          <span className="text-lg font-bold text-blue-500 mx-auto">Z</span>
        )}
        <button
          onClick={onToggle}
          className={`p-1 rounded-md transition-colors hidden lg:flex items-center justify-center ${
            isDark
              ? 'hover:bg-slate-700 text-slate-400'
              : 'hover:bg-gray-100 text-gray-500'
          } ${collapsed ? 'mx-auto' : ''}`}
          title={collapsed ? 'Expand' : 'Collapse'}
        >
          {collapsed ? (
            isRTL ? (
              <ChevronLeft className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )
          ) : isRTL ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-2 px-2 space-y-0.5">
        {items.map((item) => {
          const Icon = item.icon;
          const active = isActive(item);
          const label = lang === 'ar' ? item.label_ar : item.label_en;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.exact}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors group relative ${
                active
                  ? isDark
                    ? 'bg-blue-600/20 text-blue-400'
                    : 'bg-blue-50 text-blue-600'
                  : isDark
                  ? 'text-slate-400 hover:text-white hover:bg-slate-800'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              } ${collapsed ? 'justify-center px-2' : ''}`}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span className="truncate">{label}</span>}

              {/* Tooltip on collapsed */}
              {collapsed && (
                <span
                  className={`absolute z-50 px-2 py-1 text-xs font-medium rounded-md shadow-lg whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-200 ${
                    isDark
                      ? 'bg-slate-700 text-white'
                      : 'bg-gray-800 text-white'
                  } ${isRTL ? 'right-full mr-2' : 'left-full ml-2'}`}
                >
                  {label}
                </span>
              )}

              {/* Active indicator */}
              {active && (
                <span
                  className={`absolute top-1/2 -translate-y-1/2 w-1 h-5 rounded-full bg-blue-500 ${
                    isRTL ? 'right-0 -mr-2' : 'left-0 -ml-2'
                  }`}
                />
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom branding */}
      {!collapsed && (
        <div
          className={`px-4 py-3 border-t text-xs ${
            isDark
              ? 'border-slate-700/50 text-slate-600'
              : 'border-gray-200 text-gray-400'
          }`}
        >
          Ziyada Systems &copy; {new Date().getFullYear()}
        </div>
      )}
    </div>
  );
}
