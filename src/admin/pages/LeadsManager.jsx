import { useState, useMemo, useCallback } from "react";
import { useOutletContext } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { siteApi } from "@/api/siteApi";
import { cn } from "@/lib/utils";
import DataTable from "@/admin/components/DataTable";
import StatusBadge from "@/admin/components/StatusBadge";
import {
  Trash2,
  Download,
  Search,
  Loader2,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { format } from "date-fns";

/* ================================================================== */
/*  Bilingual labels                                                   */
/* ================================================================== */
const L = {
  ar: {
    title: "إدارة العملاء المحتملين",
    subtitle: "عرض وإدارة جميع العملاء المحتملين",
    name: "الاسم",
    email: "البريد",
    phone: "الهاتف",
    company: "الشركة",
    source: "المصدر",
    status: "الحالة",
    date: "التاريخ",
    actions: "إجراءات",
    all: "الكل",
    new: "جديد",
    contacted: "تم التواصل",
    qualified: "مؤهل",
    closed: "مغلق",
    contact: "تواصل",
    proposal: "عرض سعر",
    booking: "حجز",
    search: "بحث بالاسم أو البريد...",
    exportCsv: "تصدير CSV",
    deleteConfirm: "هل تريد حذف هذا العميل المحتمل؟",
    noResults: "لا توجد نتائج",
    statusFilter: "فلتر الحالة",
    sourceFilter: "فلتر المصدر",
    page: "صفحة",
    of: "من",
    showing: "عرض",
    to: "إلى",
    entries: "سجل",
  },
  en: {
    title: "Leads Manager",
    subtitle: "View and manage all leads",
    name: "Name",
    email: "Email",
    phone: "Phone",
    company: "Company",
    source: "Source",
    status: "Status",
    date: "Date",
    actions: "Actions",
    all: "All",
    new: "New",
    contacted: "Contacted",
    qualified: "Qualified",
    closed: "Closed",
    contact: "Contact",
    proposal: "Proposal",
    booking: "Booking",
    search: "Search by name or email...",
    exportCsv: "Export CSV",
    deleteConfirm: "Are you sure you want to delete this lead?",
    noResults: "No results found",
    statusFilter: "Status Filter",
    sourceFilter: "Source Filter",
    page: "Page",
    of: "of",
    showing: "Showing",
    to: "to",
    entries: "entries",
  },
};

const PAGE_SIZE = 10;

/* ================================================================== */
/*  LeadsManager                                                       */
/* ================================================================== */
export default function LeadsManager() {
  const { lang = "ar", theme = "dark" } = useOutletContext() || {};
  const t = L[lang] || L.ar;
  const isDark = theme === "dark";
  const isRTL = lang === "ar";
  const qc = useQueryClient();

  /* ---- Local state ---- */
  const [statusFilter, setStatusFilter] = useState("all");
  const [sourceFilter, setSourceFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  /* ---- Fetch leads ---- */
  const { data: leads = [], isLoading } = useQuery({
    queryKey: ["admin-leads"],
    queryFn: () => siteApi.entities.Lead.list("-created_at", 500),
  });

  /* ---- Mutations ---- */
  const updateMutation = useMutation({
    mutationFn: ({ id, status }) =>
      siteApi.entities.Lead.update(id, { status }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-leads"] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => siteApi.entities.Lead.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-leads"] }),
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

  const handleStatusChange = useCallback(
    (id, newStatus) => {
      updateMutation.mutate({ id, status: newStatus });
    },
    [updateMutation]
  );

  /* ---- Filtering ---- */
  const filtered = useMemo(() => {
    return leads.filter((lead) => {
      if (statusFilter !== "all" && lead.status !== statusFilter) return false;
      if (sourceFilter !== "all" && lead.source !== sourceFilter) return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const nameMatch = (lead.name || "").toLowerCase().includes(q);
        const emailMatch = (lead.email || "").toLowerCase().includes(q);
        if (!nameMatch && !emailMatch) return false;
      }
      return true;
    });
  }, [leads, statusFilter, sourceFilter, searchQuery]);

  /* ---- Pagination ---- */
  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(currentPage, totalPages);
  const startIdx = (safePage - 1) * PAGE_SIZE;
  const endIdx = startIdx + PAGE_SIZE;
  const displayed = filtered.slice(startIdx, endIdx);

  // Reset to page 1 when filters change
  const setFilterAndReset = (setter) => (value) => {
    setter(value);
    setCurrentPage(1);
  };

  /* ---- CSV Export ---- */
  const handleExport = () => {
    if (filtered.length === 0) return;
    const headers = [
      "Name",
      "Email",
      "Phone",
      "Company",
      "Source",
      "Status",
      "Date",
    ];
    const rows = filtered.map((l) => [
      l.name || "",
      l.email || "",
      l.phone || "",
      l.company || "",
      l.source || "",
      l.status || "",
      l.created_at || "",
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
    a.download = `leads_${format(new Date(), "yyyy-MM-dd")}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  /* ---- Table columns ---- */
  const columns = [
    { key: "name", label: t.name, render: (_, r) => r.name || "\u2014" },
    { key: "email", label: t.email },
    { key: "phone", label: t.phone, render: (_, r) => r.phone || "\u2014" },
    {
      key: "company",
      label: t.company,
      render: (_, r) => r.company || "\u2014",
    },
    {
      key: "source",
      label: t.source,
      render: (_, r) => <StatusBadge status={r.source} lang={lang} />,
    },
    {
      key: "status",
      label: t.status,
      render: (_, r) => (
        <select
          value={r.status || "new"}
          onChange={(e) => handleStatusChange(r.id, e.target.value)}
          className={cn(
            "rounded-lg px-2 py-1 text-xs font-semibold border cursor-pointer outline-none",
            isDark
              ? "bg-slate-700 border-white/10 text-white"
              : "bg-white border-gray-200 text-gray-700"
          )}
        >
          <option value="new">{t.new}</option>
          <option value="contacted">{t.contacted}</option>
          <option value="qualified">{t.qualified}</option>
          <option value="closed">{t.closed}</option>
        </select>
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

  const statusOptions = ["all", "new", "contacted", "qualified", "closed"];
  const sourceOptions = ["all", "contact", "proposal", "booking"];

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
        {/* Status filter */}
        <div className="flex flex-wrap gap-1.5">
          {statusOptions.map((s) => (
            <button
              key={s}
              onClick={() => setFilterAndReset(setStatusFilter)(s)}
              className={cn(
                "px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors",
                statusFilter === s
                  ? "bg-purple-600 text-white"
                  : isDark
                  ? "bg-white/8 text-gray-300 hover:bg-white/12"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              )}
            >
              {t[s] || s}
            </button>
          ))}
        </div>

        <div
          className={cn(
            "w-px h-6",
            isDark ? "bg-white/10" : "bg-gray-200"
          )}
        />

        {/* Source filter */}
        <div className="flex flex-wrap gap-1.5">
          {sourceOptions.map((s) => (
            <button
              key={s}
              onClick={() => setFilterAndReset(setSourceFilter)(s)}
              className={cn(
                "px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors",
                sourceFilter === s
                  ? "bg-cyan-600 text-white"
                  : isDark
                  ? "bg-white/8 text-gray-300 hover:bg-white/12"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              )}
            >
              {t[s] || s}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <Search
              size={15}
              className={cn(
                "absolute top-1/2 -translate-y-1/2",
                isRTL ? "right-3" : "left-3",
                isDark ? "text-gray-500" : "text-gray-400"
              )}
            />
            <input
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              placeholder={t.search}
              className={cn(
                "w-full rounded-lg border text-sm py-2 outline-none",
                isRTL ? "pr-9 pl-3" : "pl-9 pr-3",
                isDark
                  ? "bg-slate-800 border-white/10 text-white placeholder:text-gray-500"
                  : "bg-white border-gray-200 text-gray-900 placeholder:text-gray-400"
              )}
            />
          </div>
        </div>

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
        <>
          <DataTable
            columns={columns}
            data={displayed}
            theme={theme}
            lang={lang}
            emptyMessage={t.noResults}
          />

          {/* ---- Pagination ---- */}
          {filtered.length > PAGE_SIZE && (
            <div
              className={cn(
                "flex items-center justify-between mt-4 px-1"
              )}
            >
              {/* Info */}
              <p
                className={cn(
                  "text-xs",
                  isDark ? "text-gray-400" : "text-gray-500"
                )}
              >
                {t.showing} {startIdx + 1} {t.to}{" "}
                {Math.min(endIdx, filtered.length)} {t.of} {filtered.length}{" "}
                {t.entries}
              </p>

              {/* Page controls */}
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() =>
                    setCurrentPage((p) => Math.max(1, p - 1))
                  }
                  disabled={safePage <= 1}
                  className={cn(
                    "p-1.5 rounded-lg transition-colors disabled:opacity-30",
                    isDark
                      ? "hover:bg-white/10 text-gray-300"
                      : "hover:bg-gray-100 text-gray-600"
                  )}
                >
                  {isRTL ? (
                    <ChevronRight size={16} />
                  ) : (
                    <ChevronLeft size={16} />
                  )}
                </button>

                {Array.from({ length: totalPages }, (_, i) => i + 1)
                  .filter((page) => {
                    if (totalPages <= 7) return true;
                    if (page === 1 || page === totalPages) return true;
                    if (Math.abs(page - safePage) <= 1) return true;
                    return false;
                  })
                  .reduce((acc, page, idx, arr) => {
                    if (idx > 0 && page - arr[idx - 1] > 1) {
                      acc.push("...");
                    }
                    acc.push(page);
                    return acc;
                  }, [])
                  .map((item, idx) =>
                    item === "..." ? (
                      <span
                        key={`ellipsis-${idx}`}
                        className={cn(
                          "px-1 text-xs",
                          isDark ? "text-gray-500" : "text-gray-400"
                        )}
                      >
                        ...
                      </span>
                    ) : (
                      <button
                        key={item}
                        onClick={() => setCurrentPage(item)}
                        className={cn(
                          "w-8 h-8 rounded-lg text-xs font-semibold transition-colors",
                          item === safePage
                            ? "bg-purple-600 text-white"
                            : isDark
                            ? "hover:bg-white/10 text-gray-300"
                            : "hover:bg-gray-100 text-gray-600"
                        )}
                      >
                        {item}
                      </button>
                    )
                  )}

                <button
                  onClick={() =>
                    setCurrentPage((p) => Math.min(totalPages, p + 1))
                  }
                  disabled={safePage >= totalPages}
                  className={cn(
                    "p-1.5 rounded-lg transition-colors disabled:opacity-30",
                    isDark
                      ? "hover:bg-white/10 text-gray-300"
                      : "hover:bg-gray-100 text-gray-600"
                  )}
                >
                  {isRTL ? (
                    <ChevronLeft size={16} />
                  ) : (
                    <ChevronRight size={16} />
                  )}
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
