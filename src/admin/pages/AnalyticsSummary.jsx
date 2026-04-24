import { useMemo } from "react";
import { useOutletContext } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { siteApi } from "@/api/siteApi";
import { cn } from "@/lib/utils";
import StatCard from "@/admin/components/StatCard";
import {
  Users,
  BarChart3,
  ExternalLink,
  Loader2,
  TrendingUp,
  Target,
  Globe,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  LineChart,
  Line,
} from "recharts";
import { format, subDays, startOfMonth } from "date-fns";

/* ================================================================== */
/*  Bilingual labels                                                   */
/* ================================================================== */
const L = {
  ar: {
    title: "\u0645\u0644\u062E\u0635 \u0627\u0644\u062A\u062D\u0644\u064A\u0644\u0627\u062A",
    subtitle: "\u0646\u0638\u0631\u0629 \u0639\u0627\u0645\u0629 \u0639\u0644\u0649 \u0627\u0644\u0623\u062F\u0627\u0621 \u0648\u0627\u0644\u062A\u062D\u0644\u064A\u0644\u0627\u062A",
    externalDashboards: "\u0644\u0648\u062D\u0627\u062A \u0627\u0644\u062A\u062D\u0644\u064A\u0644\u0627\u062A \u0627\u0644\u062E\u0627\u0631\u062C\u064A\u0629",
    ga4: "Google Analytics",
    ga4Desc: "\u062A\u062D\u0644\u064A\u0644\u0627\u062A \u062D\u0631\u0643\u0629 \u0627\u0644\u0645\u0631\u0648\u0631 \u0648\u0627\u0644\u0645\u0633\u062A\u062E\u062F\u0645\u064A\u0646",
    posthog: "PostHog",
    posthogDesc: "\u062A\u062D\u0644\u064A\u0644\u0627\u062A \u0627\u0644\u0645\u0646\u062A\u062C \u0648\u0627\u0644\u0645\u0633\u062A\u062E\u062F\u0645\u064A\u0646",
    hotjar: "Hotjar",
    hotjarDesc: "\u062E\u0631\u0627\u0626\u0637 \u0627\u0644\u062D\u0631\u0627\u0631\u0629 \u0648\u062A\u0633\u062C\u064A\u0644\u0627\u062A \u0627\u0644\u0632\u0648\u0627\u0631",
    openDashboard: "\u0641\u062A\u062D \u0627\u0644\u0644\u0648\u062D\u0629",
    configured: "\u0645\u064F\u0641\u0639\u0651\u0644",
    notConfigured: "\u063A\u064A\u0631 \u0645\u064F\u0641\u0639\u0651\u0644",
    leadsThisMonth: "\u0639\u0645\u0644\u0627\u0621 \u0645\u062D\u062A\u0645\u0644\u064A\u0646 \u0647\u0630\u0627 \u0627\u0644\u0634\u0647\u0631",
    totalLeadsAllTime: "\u0625\u062C\u0645\u0627\u0644\u064A \u0627\u0644\u0639\u0645\u0644\u0627\u0621",
    conversionRate: "\u0645\u0639\u062F\u0644 \u0627\u0644\u062A\u062D\u0648\u064A\u0644 \u0627\u0644\u062A\u0642\u062F\u064A\u0631\u064A",
    leadsBySource: "\u0627\u0644\u0639\u0645\u0644\u0627\u0621 \u062D\u0633\u0628 \u0627\u0644\u0645\u0635\u062F\u0631",
    leadsByStatus: "\u0627\u0644\u0639\u0645\u0644\u0627\u0621 \u062D\u0633\u0628 \u0627\u0644\u062D\u0627\u0644\u0629",
    leadsPerDay: "\u0627\u0644\u0639\u0645\u0644\u0627\u0621 \u0627\u0644\u0645\u062D\u062A\u0645\u0644\u064A\u0646 \u064A\u0648\u0645\u064A\u0627\u064B (\u0622\u062E\u0631 30 \u064A\u0648\u0645)",
    noData: "\u0644\u0627 \u062A\u0648\u062C\u062F \u0628\u064A\u0627\u0646\u0627\u062A \u0643\u0627\u0641\u064A\u0629",
    source: "\u0627\u0644\u0645\u0635\u062F\u0631",
    count: "\u0627\u0644\u0639\u062F\u062F",
    contact: "\u062A\u0648\u0627\u0635\u0644",
    proposal: "\u0639\u0631\u0636 \u0633\u0639\u0631",
    booking: "\u062D\u062C\u0632",
    new: "\u062C\u062F\u064A\u062F",
    contacted: "\u062A\u0645 \u0627\u0644\u062A\u0648\u0627\u0635\u0644",
    qualified: "\u0645\u0624\u0647\u0644",
    closed: "\u0645\u063A\u0644\u0642",
    quickStats: "\u0625\u062D\u0635\u0627\u0626\u064A\u0627\u062A \u0633\u0631\u064A\u0639\u0629",
  },
  en: {
    title: "Analytics Summary",
    subtitle: "Performance overview and analytics",
    externalDashboards: "External Dashboards",
    ga4: "Google Analytics",
    ga4Desc: "Traffic and user analytics",
    posthog: "PostHog",
    posthogDesc: "Product and user analytics",
    hotjar: "Hotjar",
    hotjarDesc: "Heatmaps and session recordings",
    openDashboard: "Open Dashboard",
    configured: "Configured",
    notConfigured: "Not configured",
    leadsThisMonth: "Leads This Month",
    totalLeadsAllTime: "Total Leads (All Time)",
    conversionRate: "Est. Conversion Rate",
    leadsBySource: "Leads by Source",
    leadsByStatus: "Leads by Status",
    leadsPerDay: "Leads Per Day (Last 30 Days)",
    noData: "Not enough data",
    source: "Source",
    count: "Count",
    contact: "Contact",
    proposal: "Proposal",
    booking: "Booking",
    new: "New",
    contacted: "Contacted",
    qualified: "Qualified",
    closed: "Closed",
    quickStats: "Quick Stats",
  },
};

/* ================================================================== */
/*  Dashboard link configs                                             */
/* ================================================================== */
const DASHBOARDS = [
  {
    key: "ga4",
    envKey: "VITE_GA4_ID",
    url: "https://analytics.google.com",
    icon: BarChart3,
    color: "text-orange-400",
    bg: "bg-orange-500/10",
  },
  {
    key: "posthog",
    envKey: "VITE_POSTHOG_KEY",
    url: "https://app.posthog.com",
    icon: Target,
    color: "text-blue-400",
    bg: "bg-blue-500/10",
  },
  {
    key: "hotjar",
    envKey: "VITE_HOTJAR_ID",
    url: "https://insights.hotjar.com",
    icon: Globe,
    color: "text-red-400",
    bg: "bg-red-500/10",
  },
];

/* ================================================================== */
/*  Chart color constants                                              */
/* ================================================================== */
const SOURCE_COLORS = {
  contact: "#3b82f6",
  proposal: "#a855f7",
  booking: "#06b6d4",
};

const STATUS_COLORS = {
  new: "#3b82f6",
  contacted: "#eab308",
  qualified: "#22c55e",
  closed: "#6b7280",
};

/* ================================================================== */
/*  Component                                                          */
/* ================================================================== */
export default function AnalyticsSummary() {
  const { lang = "ar", theme = "dark" } = useOutletContext() || {};
  const t = L[lang] || L.ar;
  const isDark = theme === "dark";
  const isRTL = lang === "ar";

  /* ---- Env vars ---- */
  const ga4Id = import.meta.env.VITE_GA4_ID || "";
  const posthogKey = import.meta.env.VITE_POSTHOG_KEY || "";
  const hotjarId = import.meta.env.VITE_HOTJAR_ID || "";
  const envMap = { ga4: ga4Id, posthog: posthogKey, hotjar: hotjarId };

  /* ---- Leads query ---- */
  const { data: leads = [], isLoading } = useQuery({
    queryKey: ["admin-leads"],
    queryFn: () => siteApi.entities.Lead.list("-created_at", 500),
  });

  /* ---- Derived: Leads this month ---- */
  const monthStart = startOfMonth(new Date()).toISOString();
  const leadsThisMonth = useMemo(
    () => leads.filter((l) => (l.created_at || "") >= monthStart),
    [leads, monthStart]
  );

  /* ---- Derived: Conversion rate ---- */
  const conversionRate = useMemo(() => {
    if (leads.length === 0) return "0%";
    const converted = leads.filter(
      (l) => l.status === "qualified" || l.status === "closed"
    ).length;
    return ((converted / leads.length) * 100).toFixed(1) + "%";
  }, [leads]);

  /* ---- Derived: Leads by source (bar chart data) ---- */
  const sourceChartData = useMemo(() => {
    const counts = { contact: 0, proposal: 0, booking: 0 };
    leads.forEach((l) => {
      const src = (l.source || "").toLowerCase();
      if (src in counts) counts[src]++;
    });
    return [
      { name: t.contact, value: counts.contact, key: "contact" },
      { name: t.proposal, value: counts.proposal, key: "proposal" },
      { name: t.booking, value: counts.booking, key: "booking" },
    ];
  }, [leads, t]);

  /* ---- Derived: Leads by status (pie chart data) ---- */
  const statusChartData = useMemo(() => {
    const counts = { new: 0, contacted: 0, qualified: 0, closed: 0 };
    leads.forEach((l) => {
      const st = (l.status || "").toLowerCase();
      if (st in counts) counts[st]++;
    });
    return [
      { name: t.new, value: counts.new, key: "new" },
      { name: t.contacted, value: counts.contacted, key: "contacted" },
      { name: t.qualified, value: counts.qualified, key: "qualified" },
      { name: t.closed, value: counts.closed, key: "closed" },
    ].filter((d) => d.value > 0);
  }, [leads, t]);

  /* ---- Derived: Leads per day (last 30 days) ---- */
  const lineChartData = useMemo(() => {
    const days = [];
    const today = new Date();
    for (let i = 29; i >= 0; i--) {
      const d = subDays(today, i);
      const key = format(d, "yyyy-MM-dd");
      days.push({ date: key, label: format(d, "MM/dd"), count: 0 });
    }
    leads.forEach((l) => {
      if (!l.created_at) return;
      try {
        const dateStr = l.created_at.split("T")[0];
        const dayEntry = days.find((d) => d.date === dateStr);
        if (dayEntry) dayEntry.count++;
      } catch {
        // skip
      }
    });
    return days;
  }, [leads]);

  /* ---- Tooltip styles ---- */
  const tooltipStyle = {
    background: isDark ? "#1e293b" : "#fff",
    border: `1px solid ${isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)"}`,
    borderRadius: 8,
    fontSize: 13,
    color: isDark ? "#f8fafc" : "#0f172a",
  };

  const axisTickStyle = { fill: isDark ? "#6b7280" : "#9ca3af", fontSize: 11 };
  const axisLineStyle = {
    stroke: isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)",
  };
  const gridStroke = isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.06)";

  /* ---- Card class ---- */
  const cardCls = cn(
    "rounded-xl border p-6",
    isDark ? "bg-slate-800/60 border-white/10" : "bg-white border-gray-200 shadow-sm"
  );

  return (
    <div className="max-w-7xl mx-auto" dir={isRTL ? "rtl" : "ltr"}>
      {/* Header */}
      <div className="mb-8">
        <h1 className={cn("text-3xl font-black", isDark ? "text-white" : "text-gray-900")}>
          {t.title}
        </h1>
        <p className={cn("text-sm mt-1", isDark ? "text-gray-400" : "text-gray-500")}>
          {t.subtitle}
        </p>
      </div>

      {/* External Dashboards */}
      <div className="mb-8">
        <h2 className={cn("text-lg font-bold mb-3", isDark ? "text-white" : "text-gray-900")}>
          {t.externalDashboards}
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {DASHBOARDS.map((dash) => {
            const isConfigured = !!envMap[dash.key];
            return (
              <a
                key={dash.key}
                href={dash.url}
                target="_blank"
                rel="noopener noreferrer"
                className={cn(
                  "rounded-xl border p-5 flex items-center gap-4 transition-colors group",
                  isDark
                    ? "bg-slate-800/60 border-white/10 hover:bg-slate-800/80"
                    : "bg-white border-gray-200 hover:bg-gray-50 shadow-sm"
                )}
              >
                <div className={cn("w-11 h-11 rounded-lg flex items-center justify-center", dash.bg)}>
                  <dash.icon size={20} className={dash.color} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className={cn("font-bold text-sm", isDark ? "text-white" : "text-gray-900")}>
                    {t[dash.key]}
                  </div>
                  <div className={cn("text-xs mt-0.5", isDark ? "text-gray-500" : "text-gray-400")}>
                    {t[dash.key + "Desc"]}
                  </div>
                  <div className="flex items-center gap-1 mt-1.5">
                    {isConfigured ? (
                      <>
                        <CheckCircle2 size={12} className="text-green-500" />
                        <span className="text-[10px] font-semibold text-green-500">
                          {t.configured}
                          {dash.key === "ga4" && ga4Id ? ` (${ga4Id})` : ""}
                        </span>
                      </>
                    ) : (
                      <>
                        <XCircle size={12} className="text-gray-500" />
                        <span className={cn("text-[10px] font-semibold", isDark ? "text-gray-500" : "text-gray-400")}>
                          {t.notConfigured}
                        </span>
                      </>
                    )}
                  </div>
                </div>
                <ExternalLink
                  size={16}
                  className={cn(
                    "transition-transform group-hover:translate-x-0.5 flex-shrink-0",
                    isDark ? "text-gray-600" : "text-gray-300"
                  )}
                />
              </a>
            );
          })}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="mb-8">
        <h2 className={cn("text-lg font-bold mb-3", isDark ? "text-white" : "text-gray-900")}>
          {t.quickStats}
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <StatCard
            title={t.leadsThisMonth}
            value={leadsThisMonth.length}
            icon={Users}
            color="purple"
            loading={isLoading}
            theme={theme}
            lang={lang}
          />
          <StatCard
            title={t.totalLeadsAllTime}
            value={leads.length}
            icon={TrendingUp}
            color="blue"
            loading={isLoading}
            theme={theme}
            lang={lang}
          />
          <StatCard
            title={t.conversionRate}
            value={conversionRate}
            icon={Target}
            color="green"
            loading={isLoading}
            theme={theme}
            lang={lang}
          />
        </div>
      </div>

      {/* Charts Row: Source bar chart + Status pie chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Leads by Source (Bar Chart) */}
        <div>
          <h2 className={cn("text-lg font-bold mb-3", isDark ? "text-white" : "text-gray-900")}>
            {t.leadsBySource}
          </h2>
          <div className={cardCls}>
            {isLoading ? (
              <div className="flex justify-center py-16">
                <Loader2 className="animate-spin text-purple-500" size={28} />
              </div>
            ) : sourceChartData.every((d) => d.value === 0) ? (
              <div className={cn("flex items-center justify-center py-16 text-sm", isDark ? "text-gray-500" : "text-gray-400")}>
                {t.noData}
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={sourceChartData} barSize={48}>
                  <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                  <XAxis
                    dataKey="name"
                    tick={axisTickStyle}
                    axisLine={axisLineStyle}
                    tickLine={false}
                  />
                  <YAxis
                    allowDecimals={false}
                    tick={axisTickStyle}
                    axisLine={axisLineStyle}
                    tickLine={false}
                  />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                    {sourceChartData.map((entry) => (
                      <Cell
                        key={entry.key}
                        fill={SOURCE_COLORS[entry.key] || "#7c3aed"}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Leads by Status (Pie/Donut Chart) */}
        <div>
          <h2 className={cn("text-lg font-bold mb-3", isDark ? "text-white" : "text-gray-900")}>
            {t.leadsByStatus}
          </h2>
          <div className={cardCls}>
            {isLoading ? (
              <div className="flex justify-center py-16">
                <Loader2 className="animate-spin text-purple-500" size={28} />
              </div>
            ) : statusChartData.length === 0 ? (
              <div className={cn("flex items-center justify-center py-16 text-sm", isDark ? "text-gray-500" : "text-gray-400")}>
                {t.noData}
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={statusChartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={95}
                    paddingAngle={3}
                    strokeWidth={0}
                  >
                    {statusChartData.map((entry) => (
                      <Cell
                        key={entry.key}
                        fill={STATUS_COLORS[entry.key] || "#6b7280"}
                      />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={tooltipStyle} />
                  <Legend
                    verticalAlign="bottom"
                    height={36}
                    formatter={(value) => (
                      <span className={isDark ? "text-gray-300" : "text-gray-600"} style={{ fontSize: 12 }}>
                        {value}
                      </span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Chart: Leads per day (line chart) */}
      <div className="mb-8">
        <h2 className={cn("text-lg font-bold mb-3", isDark ? "text-white" : "text-gray-900")}>
          {t.leadsPerDay}
        </h2>
        <div className={cardCls}>
          {isLoading ? (
            <div className="flex justify-center py-16">
              <Loader2 className="animate-spin text-purple-500" size={28} />
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={lineChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                <XAxis
                  dataKey="label"
                  tick={axisTickStyle}
                  axisLine={axisLineStyle}
                  tickLine={false}
                  interval="preserveStartEnd"
                />
                <YAxis
                  allowDecimals={false}
                  tick={axisTickStyle}
                  axisLine={axisLineStyle}
                  tickLine={false}
                />
                <Tooltip contentStyle={tooltipStyle} />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#7c3aed"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 5, fill: "#7c3aed" }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}
