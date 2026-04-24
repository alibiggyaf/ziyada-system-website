import { useState, useMemo, useCallback } from "react";
import { useOutletContext } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { siteApi } from "@/api/siteApi";
import { cn } from "@/lib/utils";
import DataTable from "@/admin/components/DataTable";
import StatusBadge from "@/admin/components/StatusBadge";
import { Trash2, Download, Loader2 } from "lucide-react";
import { format } from "date-fns";

/* ================================================================== */
/*  Bilingual labels                                                   */
/* ================================================================== */
const L = {
  ar: {
    title: "إدارة المشتركين",
    subtitle: "عرض قائمة المشتركين في النشرة البريدية",
    email: "البريد الإلكتروني",
    name: "الاسم",
    language: "اللغة",
    status: "الحالة",
    date: "التاريخ",
    actions: "إجراءات",
    all: "الكل",
    active: "نشط",
    unsubscribed: "ملغي الاشتراك",
    exportCsv: "تصدير CSV",
    deleteConfirm: "هل تريد حذف هذا المشترك؟",
    noResults: "لا يوجد مشتركين",
  },
  en: {
    title: "Subscribers Manager",
    subtitle: "View newsletter subscriber list",
    email: "Email",
    name: "Name",
    language: "Language",
    status: "Status",
    date: "Date",
    actions: "Actions",
    all: "All",
    active: "Active",
    unsubscribed: "Unsubscribed",
    exportCsv: "Export CSV",
    deleteConfirm: "Are you sure you want to delete this subscriber?",
    noResults: "No subscribers found",
  },
};

/* ================================================================== */
/*  SubscribersManager                                                 */
/* ================================================================== */
export default function SubscribersManager() {
  const { lang = "ar", theme = "dark" } = useOutletContext() || {};
  const t = L[lang] || L.ar;
  const isDark = theme === "dark";
  const isRTL = lang === "ar";
  const qc = useQueryClient();

  /* ---- Local state ---- */
  const [statusFilter, setStatusFilter] = useState("all");

  /* ---- Fetch subscribers ---- */
  const { data: subscribers = [], isLoading } = useQuery({
    queryKey: ["admin-subscribers"],
    queryFn: () => siteApi.entities.Subscriber.list("-created_at", 500),
  });

  /* ---- Mutations ---- */
  const deleteMutation = useMutation({
    mutationFn: (id) => siteApi.entities.Subscriber.delete(id),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["admin-subscribers"] }),
  });

  /* ---- Handlers ---- */
  const handleDelete = useCallback(
    (id) => {
      if (window.confirm(t.deleteConfirm)) {
        deleteMutation.mutate(id);
      }
    },
    [t.deleteConfirm, deleteMutation]
  );

  /* ---- Filtering ---- */
  const filtered = useMemo(() => {
    if (statusFilter === "all") return subscribers;
    return subscribers.filter((s) => s.status === statusFilter);
  }, [subscribers, statusFilter]);

  /* ---- CSV Export ---- */
  const handleExport = () => {
    if (filtered.length === 0) return;
    const headers = ["Email", "Name", "Language", "Status", "Date"];
    const rows = filtered.map((s) => [
      s.email || "",
      s.name || "",
      s.language || "",
      s.status || "",
      s.created_at || "",
    ]);
    const csv = [headers, ...rows]
      .map((r) =>
        r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(",")
      )
      .join("\n");
    const blob = new Blob(["\uFEFF" + csv], {
      type: "text/csv;charset=utf-8;",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `subscribers_${format(new Date(), "yyyy-MM-dd")}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  /* ---- Table columns ---- */
  const columns = [
    { key: "email", label: t.email },
    { key: "name", label: t.name, render: (_, r) => r.name || "\u2014" },
    {
      key: "language",
      label: t.language,
      render: (_, r) => (
        <span
          className={cn(
            "inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider",
            isDark
              ? "bg-white/10 text-gray-300"
              : "bg-gray-100 text-gray-600"
          )}
        >
          {(r.language || "ar").toUpperCase()}
        </span>
      ),
    },
    {
      key: "status",
      label: t.status,
      render: (_, r) => (
        <StatusBadge status={r.status || "active"} lang={lang} />
      ),
    },
    {
      key: "date",
      label: t.date,
      render: (_, r) => {
        try {
          return format(new Date(r.created_at), "yyyy-MM-dd");
        } catch {
          return "\u2014";
        }
      },
    },
    {
      key: "actions",
      label: t.actions,
      render: (_, r) => (
        <button
          onClick={() => handleDelete(r.id)}
          disabled={deleteMutation.isPending}
          className="rounded-lg p-2 text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-40"
        >
          <Trash2 size={15} />
        </button>
      ),
    },
  ];

  const statusOptions = ["all", "active", "unsubscribed"];

  /* ---- Filter badge accents ---- */
  const filterAccent = {
    all: "bg-purple-600",
    active: "bg-green-600",
    unsubscribed: "bg-gray-600",
  };

  return (
    <div className="max-w-7xl mx-auto" dir={isRTL ? "rtl" : "ltr"}>
      {/* ---- Header ---- */}
      <div className="mb-6">
        <h1
          className={cn(
            "text-3xl font-black",
            isDark ? "text-white" : "text-gray-900"
          )}
        >
          {t.title}
        </h1>
        <p
          className={cn(
            "text-sm mt-1",
            isDark ? "text-gray-400" : "text-gray-500"
          )}
        >
          {t.subtitle}
        </p>
      </div>

      {/* ---- Filter bar ---- */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
        <div className="flex flex-wrap gap-1.5">
          {statusOptions.map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={cn(
                "px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors",
                statusFilter === s
                  ? `${filterAccent[s] || "bg-purple-600"} text-white`
                  : isDark
                  ? "bg-white/8 text-gray-300 hover:bg-white/12"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              )}
            >
              {t[s] || s}
            </button>
          ))}
        </div>

        {/* Count badge */}
        <span
          className={cn(
            "text-xs font-medium px-2 py-0.5 rounded-full",
            isDark
              ? "bg-white/10 text-gray-400"
              : "bg-gray-100 text-gray-500"
          )}
        >
          {filtered.length}
        </span>

        <div className="flex-1" />

        {/* Export */}
        <button
          onClick={handleExport}
          className={cn(
            "inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-colors",
            isDark
              ? "bg-white/10 text-white hover:bg-white/15"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          )}
        >
          <Download size={15} /> {t.exportCsv}
        </button>
      </div>

      {/* ---- Table ---- */}
      {isLoading ? (
        <div
          className={cn(
            "rounded-xl border p-16 flex justify-center",
            isDark
              ? "bg-slate-800/60 border-white/10"
              : "bg-white border-gray-200"
          )}
        >
          <Loader2 className="animate-spin text-purple-500" size={28} />
        </div>
      ) : (
        <DataTable
          columns={columns}
          data={filtered}
          theme={theme}
          lang={lang}
          emptyMessage={t.noResults}
        />
      )}
    </div>
  );
}
