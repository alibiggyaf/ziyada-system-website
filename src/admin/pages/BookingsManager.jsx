import { useState, useMemo, useCallback } from "react";
import { useOutletContext } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { siteApi } from "@/api/siteApi";
import { cn } from "@/lib/utils";
import DataTable from "@/admin/components/DataTable";
import StatusBadge from "@/admin/components/StatusBadge";
import { Trash2, Loader2, ExternalLink } from "lucide-react";

/* ================================================================== */
/*  Bilingual labels                                                   */
/* ================================================================== */
const L = {
  ar: {
    title: "إدارة الحجوزات",
    subtitle: "عرض وإدارة جميع الحجوزات",
    name: "الاسم",
    email: "البريد",
    company: "الشركة",
    date: "التاريخ",
    time: "الوقت",
    status: "الحالة",
    meetLink: "رابط الاجتماع",
    actions: "إجراءات",
    all: "الكل",
    pending: "قيد الانتظار",
    confirmed: "مؤكد",
    cancelled: "ملغي",
    deleteConfirm: "هل تريد حذف هذا الحجز؟",
    noResults: "لا توجد حجوزات",
    join: "انضمام",
    noLink: "\u2014",
  },
  en: {
    title: "Bookings Manager",
    subtitle: "View and manage all bookings",
    name: "Name",
    email: "Email",
    company: "Company",
    date: "Date",
    time: "Time",
    status: "Status",
    meetLink: "Meet Link",
    actions: "Actions",
    all: "All",
    pending: "Pending",
    confirmed: "Confirmed",
    cancelled: "Cancelled",
    deleteConfirm: "Are you sure you want to delete this booking?",
    noResults: "No bookings found",
    join: "Join",
    noLink: "\u2014",
  },
};

/* ================================================================== */
/*  BookingsManager                                                    */
/* ================================================================== */
export default function BookingsManager() {
  const { lang = "ar", theme = "dark" } = useOutletContext() || {};
  const t = L[lang] || L.ar;
  const isDark = theme === "dark";
  const isRTL = lang === "ar";
  const qc = useQueryClient();

  /* ---- Local state ---- */
  const [statusFilter, setStatusFilter] = useState("all");

  /* ---- Fetch bookings ---- */
  const { data: bookings = [], isLoading } = useQuery({
    queryKey: ["admin-bookings"],
    queryFn: () => siteApi.entities.Booking.list("-created_at", 500),
  });

  /* ---- Mutations ---- */
  const updateMutation = useMutation({
    mutationFn: ({ id, status }) =>
      siteApi.entities.Booking.update(id, { status }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-bookings"] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => siteApi.entities.Booking.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-bookings"] }),
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
    if (statusFilter === "all") return bookings;
    return bookings.filter((b) => b.status === statusFilter);
  }, [bookings, statusFilter]);

  /* ---- Table columns ---- */
  const columns = [
    {
      key: "name",
      label: t.name,
      render: (_, r) => r.lead_name || r.name || "\u2014",
    },
    {
      key: "email",
      label: t.email,
      render: (_, r) => r.lead_email || r.email || "\u2014",
    },
    {
      key: "company",
      label: t.company,
      render: (_, r) => r.company || "\u2014",
    },
    {
      key: "booking_date",
      label: t.date,
      render: (_, r) => r.booking_date || "\u2014",
    },
    {
      key: "booking_time",
      label: t.time,
      render: (_, r) => r.booking_time || "\u2014",
    },
    {
      key: "status",
      label: t.status,
      render: (_, r) => (
        <select
          value={r.status || "pending"}
          onChange={(e) => handleStatusChange(r.id, e.target.value)}
          className={cn(
            "rounded-lg px-2 py-1 text-xs font-semibold border cursor-pointer outline-none",
            isDark
              ? "bg-slate-700 border-white/10 text-white"
              : "bg-white border-gray-200 text-gray-700"
          )}
        >
          <option value="pending">{t.pending}</option>
          <option value="confirmed">{t.confirmed}</option>
          <option value="cancelled">{t.cancelled}</option>
        </select>
      ),
    },
    {
      key: "meet_link",
      label: t.meetLink,
      render: (_, r) => {
        const link = r.meet_link || r.meeting_link;
        if (!link) return <span className="text-gray-500">{t.noLink}</span>;
        return (
          <a
            href={link}
            target="_blank"
            rel="noopener noreferrer"
            className={cn(
              "inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-lg transition-colors",
              "bg-blue-500/15 text-blue-400 hover:bg-blue-500/25"
            )}
          >
            <ExternalLink size={12} />
            {t.join}
          </a>
        );
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

  const statusOptions = ["all", "pending", "confirmed", "cancelled"];

  /* ---- Status filter badge colors ---- */
  const filterAccent = {
    all: "bg-purple-600",
    pending: "bg-yellow-600",
    confirmed: "bg-green-600",
    cancelled: "bg-red-600",
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
      <div className="flex flex-wrap items-center gap-2 mb-6">
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
