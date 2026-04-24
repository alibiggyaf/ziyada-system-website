const STATUS_COLORS = {
  new: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
  contacted: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30',
  qualified: 'bg-green-500/15 text-green-400 border-green-500/30',
  closed: 'bg-gray-500/15 text-gray-400 border-gray-500/30',
  pending: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30',
  confirmed: 'bg-green-500/15 text-green-400 border-green-500/30',
  cancelled: 'bg-red-500/15 text-red-400 border-red-500/30',
  published: 'bg-green-500/15 text-green-400 border-green-500/30',
  draft: 'bg-gray-500/15 text-gray-400 border-gray-500/30',
  active: 'bg-green-500/15 text-green-400 border-green-500/30',
  unsubscribed: 'bg-gray-500/15 text-gray-400 border-gray-500/30',
  contact: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
  proposal: 'bg-purple-500/15 text-purple-400 border-purple-500/30',
  booking: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30',
};

const LABELS_AR = {
  new: '\u062C\u062F\u064A\u062F',
  contacted: '\u062A\u0645 \u0627\u0644\u062A\u0648\u0627\u0635\u0644',
  qualified: '\u0645\u0624\u0647\u0644',
  closed: '\u0645\u063A\u0644\u0642',
  pending: '\u0642\u064A\u062F \u0627\u0644\u0627\u0646\u062A\u0638\u0627\u0631',
  confirmed: '\u0645\u0624\u0643\u062F',
  cancelled: '\u0645\u0644\u063A\u064A',
  published: '\u0645\u0646\u0634\u0648\u0631',
  draft: '\u0645\u0633\u0648\u062F\u0629',
  active: '\u0646\u0634\u0637',
  unsubscribed: '\u0645\u0644\u063A\u064A \u0627\u0644\u0627\u0634\u062A\u0631\u0627\u0643',
  contact: '\u062A\u0648\u0627\u0635\u0644',
  proposal: '\u0639\u0631\u0636 \u0633\u0639\u0631',
  booking: '\u062D\u062C\u0632',
};

const SIZE_CLASSES = {
  sm: 'px-2 py-0.5 text-[10px]',
  md: 'px-2.5 py-0.5 text-xs',
};

export default function StatusBadge({ status, size = 'sm', lang }) {
  if (!status) return null;

  const key = status.toLowerCase();

  const colorClasses =
    STATUS_COLORS[key] || 'bg-gray-500/15 text-gray-400 border-gray-500/30';

  const sizeClasses = SIZE_CLASSES[size] || SIZE_CLASSES.sm;

  const label =
    lang === 'ar'
      ? LABELS_AR[key] || status
      : status.charAt(0).toUpperCase() + status.slice(1).toLowerCase();

  return (
    <span
      className={`inline-flex items-center rounded-full font-bold border whitespace-nowrap ${colorClasses} ${sizeClasses}`}
    >
      {label}
    </span>
  );
}
