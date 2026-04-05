const COLOR_MAP = {
  blue: {
    border: 'border-l-blue-500',
    borderR: 'border-r-blue-500',
    iconBg: 'bg-blue-500/20',
    text: 'text-blue-400',
    gradient: 'from-blue-500/5 to-transparent',
    lightBorder: 'border-l-blue-500',
    lightBorderR: 'border-r-blue-500',
    lightIconBg: 'bg-blue-100',
    lightText: 'text-blue-600',
    lightGradient: 'from-blue-50/80 to-transparent',
  },
  green: {
    border: 'border-l-green-500',
    borderR: 'border-r-green-500',
    iconBg: 'bg-green-500/20',
    text: 'text-green-400',
    gradient: 'from-green-500/5 to-transparent',
    lightBorder: 'border-l-green-500',
    lightBorderR: 'border-r-green-500',
    lightIconBg: 'bg-green-100',
    lightText: 'text-green-600',
    lightGradient: 'from-green-50/80 to-transparent',
  },
  purple: {
    border: 'border-l-purple-500',
    borderR: 'border-r-purple-500',
    iconBg: 'bg-purple-500/20',
    text: 'text-purple-400',
    gradient: 'from-purple-500/5 to-transparent',
    lightBorder: 'border-l-purple-500',
    lightBorderR: 'border-r-purple-500',
    lightIconBg: 'bg-purple-100',
    lightText: 'text-purple-600',
    lightGradient: 'from-purple-50/80 to-transparent',
  },
  orange: {
    border: 'border-l-orange-500',
    borderR: 'border-r-orange-500',
    iconBg: 'bg-orange-500/20',
    text: 'text-orange-400',
    gradient: 'from-orange-500/5 to-transparent',
    lightBorder: 'border-l-orange-500',
    lightBorderR: 'border-r-orange-500',
    lightIconBg: 'bg-orange-100',
    lightText: 'text-orange-600',
    lightGradient: 'from-orange-50/80 to-transparent',
  },
  amber: {
    border: 'border-l-amber-500',
    borderR: 'border-r-amber-500',
    iconBg: 'bg-amber-500/20',
    text: 'text-amber-400',
    gradient: 'from-amber-500/5 to-transparent',
    lightBorder: 'border-l-amber-500',
    lightBorderR: 'border-r-amber-500',
    lightIconBg: 'bg-amber-100',
    lightText: 'text-amber-600',
    lightGradient: 'from-amber-50/80 to-transparent',
  },
  cyan: {
    border: 'border-l-cyan-500',
    borderR: 'border-r-cyan-500',
    iconBg: 'bg-cyan-500/20',
    text: 'text-cyan-400',
    gradient: 'from-cyan-500/5 to-transparent',
    lightBorder: 'border-l-cyan-500',
    lightBorderR: 'border-r-cyan-500',
    lightIconBg: 'bg-cyan-100',
    lightText: 'text-cyan-600',
    lightGradient: 'from-cyan-50/80 to-transparent',
  },
  red: {
    border: 'border-l-red-500',
    borderR: 'border-r-red-500',
    iconBg: 'bg-red-500/20',
    text: 'text-red-400',
    gradient: 'from-red-500/5 to-transparent',
    lightBorder: 'border-l-red-500',
    lightBorderR: 'border-r-red-500',
    lightIconBg: 'bg-red-100',
    lightText: 'text-red-600',
    lightGradient: 'from-red-50/80 to-transparent',
  },
};

export default function StatCard({
  title,
  label,
  value,
  icon: Icon,
  color = 'blue',
  subtitle,
  loading,
  isDark: isDarkProp,
  isRTL: isRTLProp,
  theme,
  lang,
}) {
  const isDark = isDarkProp ?? theme === 'dark';
  const isRTL = isRTLProp ?? lang === 'ar';
  const c = COLOR_MAP[color] || COLOR_MAP.blue;
  const displayTitle = title || label;

  // Use RTL-aware border side
  const borderSide = isRTL
    ? `border-r-4 ${isDark ? c.borderR : c.lightBorderR}`
    : `border-l-4 ${isDark ? c.border : c.lightBorder}`;

  return (
    <div
      className={`relative overflow-hidden rounded-xl border p-5 backdrop-blur-sm transition-colors ${borderSide} ${
        isDark
          ? 'bg-slate-800/60 border-white/10'
          : 'bg-white border-gray-200 shadow-sm'
      }`}
    >
      {/* Subtle gradient background */}
      <div
        className={`absolute inset-0 bg-gradient-to-br pointer-events-none ${
          isDark ? c.gradient : c.lightGradient
        }`}
      />

      <div className="relative flex items-center gap-4">
        {/* Icon */}
        {Icon && (
          <div
            className={`w-11 h-11 rounded-lg flex items-center justify-center flex-shrink-0 ${
              isDark ? c.iconBg : c.lightIconBg
            }`}
          >
            <Icon
              size={20}
              className={isDark ? c.text : c.lightText}
            />
          </div>
        )}

        {/* Content */}
        <div className="min-w-0 flex-1">
          {loading ? (
            <div
              className={`h-7 w-16 rounded animate-pulse ${
                isDark ? 'bg-white/10' : 'bg-gray-200'
              }`}
            />
          ) : (
            <div
              className={`text-2xl font-black ${
                isDark ? 'text-white' : 'text-gray-900'
              }`}
            >
              {value ?? 0}
            </div>
          )}
          <div
            className={`text-xs font-medium mt-0.5 ${
              isDark ? 'text-gray-400' : 'text-gray-500'
            }`}
          >
            {displayTitle}
          </div>
        </div>
      </div>

      {/* Subtitle */}
      {subtitle && (
        <p
          className={`relative text-xs mt-3 pt-3 border-t ${
            isDark
              ? 'text-gray-500 border-white/5'
              : 'text-gray-400 border-gray-100'
          }`}
        >
          {subtitle}
        </p>
      )}
    </div>
  );
}
