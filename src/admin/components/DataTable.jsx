import { ArrowUp, ArrowDown } from 'lucide-react';

export default function DataTable({
  columns,
  data,
  onSort,
  sortColumn,
  sortDirection,
  loading,
  emptyMessage,
  isDark: isDarkProp,
  isRTL: isRTLProp,
  theme,
  lang,
}) {
  const isDark = isDarkProp ?? theme === 'dark';
  const isRTL = isRTLProp ?? lang === 'ar';
  const textAlign = isRTL ? 'text-right' : 'text-left';

  const containerCls = `overflow-x-auto rounded-xl border ${
    isDark ? 'bg-slate-800/60 border-white/10' : 'bg-white border-gray-200 shadow-sm'
  }`;

  const headerRowCls = `border-b ${isDark ? 'border-white/10' : 'border-gray-100'}`;

  const headerCellCls = (col) =>
    `px-4 py-3 text-xs font-bold uppercase tracking-wider ${textAlign} ${
      isDark ? 'text-gray-400' : 'text-gray-500'
    } ${col.className || ''}`;

  // Loading skeleton
  if (loading) {
    return (
      <div className={containerCls} dir={isRTL ? 'rtl' : 'ltr'}>
        <table className="w-full text-sm">
          <thead className="sticky top-0 z-10">
            <tr className={`${headerRowCls} ${isDark ? 'bg-slate-800/90 backdrop-blur-sm' : 'bg-white'}`}>
              {columns.map((col) => (
                <th key={col.key} className={headerCellCls(col)}>
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: 5 }).map((_, rowIdx) => (
              <tr
                key={rowIdx}
                className={`border-b ${isDark ? 'border-white/5' : 'border-gray-50'}`}
              >
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-3">
                    <div
                      className={`h-4 rounded animate-pulse ${
                        rowIdx % 2 === 0 ? 'w-3/4' : 'w-1/2'
                      } ${isDark ? 'bg-white/10' : 'bg-gray-200'}`}
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  // Empty state
  if (!data || data.length === 0) {
    return (
      <div className={containerCls} dir={isRTL ? 'rtl' : 'ltr'}>
        <table className="w-full text-sm">
          <thead className="sticky top-0 z-10">
            <tr className={`${headerRowCls} ${isDark ? 'bg-slate-800/90 backdrop-blur-sm' : 'bg-white'}`}>
              {columns.map((col) => (
                <th key={col.key} className={headerCellCls(col)}>
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
        </table>
        <div
          className={`flex items-center justify-center py-16 text-sm ${
            isDark ? 'text-gray-500' : 'text-gray-400'
          }`}
        >
          {emptyMessage || (isRTL ? '\u0644\u0627 \u062A\u0648\u062C\u062F \u0628\u064A\u0627\u0646\u0627\u062A' : 'No data available')}
        </div>
      </div>
    );
  }

  return (
    <div className={containerCls} dir={isRTL ? 'rtl' : 'ltr'}>
      <table className="w-full text-sm">
        <thead className="sticky top-0 z-10">
          <tr className={`${headerRowCls} ${isDark ? 'bg-slate-800/90 backdrop-blur-sm' : 'bg-white'}`}>
            {columns.map((col) => {
              const isSorted = sortColumn === col.key;
              const canSort = !!onSort;

              return (
                <th
                  key={col.key}
                  className={`${headerCellCls(col)} transition-colors ${
                    canSort
                      ? `cursor-pointer ${
                          isDark ? 'hover:text-white' : 'hover:text-gray-900'
                        }`
                      : ''
                  }`}
                  onClick={() => canSort && onSort(col.key)}
                >
                  <div className="flex items-center gap-1">
                    <span>{col.label}</span>
                    {canSort && isSorted && (
                      sortDirection === 'asc' ? (
                        <ArrowUp className="w-3.5 h-3.5" />
                      ) : (
                        <ArrowDown className="w-3.5 h-3.5" />
                      )
                    )}
                  </div>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIdx) => (
            <tr
              key={row.id || rowIdx}
              className={`border-b last:border-b-0 transition-colors ${
                rowIdx % 2 === 0
                  ? 'bg-transparent'
                  : isDark
                  ? 'bg-white/[0.02]'
                  : 'bg-gray-50/50'
              } ${
                isDark
                  ? 'border-white/5 hover:bg-white/5'
                  : 'border-gray-50 hover:bg-gray-50'
              }`}
            >
              {columns.map((col) => (
                <td
                  key={col.key}
                  className={`px-4 py-3 ${textAlign} ${col.className || ''} ${
                    isDark ? 'text-gray-200' : 'text-gray-700'
                  }`}
                >
                  {col.render
                    ? col.render(row[col.key], row)
                    : row[col.key] ?? '\u2014'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
