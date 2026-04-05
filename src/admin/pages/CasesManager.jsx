import { useState, useCallback } from "react";
import { useOutletContext } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { siteApi } from "@/api/siteApi";
import { cn } from "@/lib/utils";
import StatusBadge from "@/admin/components/StatusBadge";
import {
  Plus,
  Edit,
  Trash2,
  Eye,
  EyeOff,
  X,
  Save,
  Loader2,
  Briefcase,
  Image,
} from "lucide-react";

/* ================================================================== */
/*  Bilingual labels                                                   */
/* ================================================================== */
const L = {
  ar: {
    title: "إدارة دراسات الحالة",
    subtitle: "عرض وإدارة جميع دراسات الحالة",
    newCase: "دراسة حالة جديدة",
    editCase: "تعديل دراسة الحالة",
    titleLabel: "العنوان",
    client: "العميل",
    industry: "القطاع",
    published: "منشور",
    order: "الترتيب",
    actions: "إجراءات",
    titleAr: "العنوان (عربي)",
    titleEn: "العنوان (إنجليزي)",
    challengeAr: "التحدي (عربي)",
    challengeEn: "التحدي (إنجليزي)",
    solutionAr: "الحل (عربي)",
    solutionEn: "الحل (إنجليزي)",
    coverImage: "رابط صورة الغلاف",
    displayOrder: "ترتيب العرض",
    save: "حفظ",
    saving: "جاري الحفظ...",
    cancel: "إلغاء",
    deleteConfirm: "هل تريد حذف دراسة الحالة هذه؟",
    noResults: "لا توجد دراسات حالة",
    publish: "نشر",
    unpublish: "إلغاء النشر",
    totalCases: "إجمالي الدراسات",
    publishedCount: "منشور",
    challenge: "التحدي",
    solution: "الحل",
    details: "التفاصيل",
  },
  en: {
    title: "Cases Manager",
    subtitle: "View and manage all case studies",
    newCase: "New Case Study",
    editCase: "Edit Case Study",
    titleLabel: "Title",
    client: "Client",
    industry: "Industry",
    published: "Published",
    order: "Order",
    actions: "Actions",
    titleAr: "Title (Arabic)",
    titleEn: "Title (English)",
    challengeAr: "Challenge (Arabic)",
    challengeEn: "Challenge (English)",
    solutionAr: "Solution (Arabic)",
    solutionEn: "Solution (English)",
    coverImage: "Cover Image URL",
    displayOrder: "Display Order",
    save: "Save",
    saving: "Saving...",
    cancel: "Cancel",
    deleteConfirm: "Are you sure you want to delete this case study?",
    noResults: "No case studies found",
    publish: "Publish",
    unpublish: "Unpublish",
    totalCases: "Total Cases",
    publishedCount: "Published",
    challenge: "Challenge",
    solution: "Solution",
    details: "Details",
  },
};

/* ================================================================== */
/*  Blank form template                                                */
/* ================================================================== */
const BLANK = {
  title_ar: "",
  title_en: "",
  client: "",
  industry: "",
  challenge_ar: "",
  challenge_en: "",
  solution_ar: "",
  solution_en: "",
  cover_image: "",
  published: true,
  display_order: 0,
};

/* ================================================================== */
/*  CasesManager                                                       */
/* ================================================================== */
export default function CasesManager() {
  const { lang = "ar", theme = "dark" } = useOutletContext() || {};
  const t = L[lang] || L.ar;
  const isDark = theme === "dark";
  const isRTL = lang === "ar";
  const qc = useQueryClient();

  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(BLANK);
  const [showDialog, setShowDialog] = useState(false);

  /* ---- Fetch cases ---- */
  const { data: cases = [], isLoading } = useQuery({
    queryKey: ["admin-cases"],
    queryFn: () => siteApi.entities.CaseStudy.list("display_order", 100),
  });

  /* ---- Mutations ---- */
  const saveMutation = useMutation({
    mutationFn: () => {
      if (editing === "new") {
        return siteApi.entities.CaseStudy.create(form);
      }
      return siteApi.entities.CaseStudy.update(editing, form);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-cases"] });
      closeDialog();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => siteApi.entities.CaseStudy.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-cases"] }),
  });

  const togglePublishMutation = useMutation({
    mutationFn: ({ id, published }) =>
      siteApi.entities.CaseStudy.update(id, { published: !published }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-cases"] }),
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

  const openNew = () => {
    setEditing("new");
    setForm({ ...BLANK, display_order: cases.length });
    setShowDialog(true);
  };

  const openEdit = (item) => {
    setEditing(item.id);
    setForm({
      title_ar: item.title_ar || "",
      title_en: item.title_en || "",
      client: item.client || "",
      industry: item.industry || "",
      challenge_ar: item.challenge_ar || "",
      challenge_en: item.challenge_en || "",
      solution_ar: item.solution_ar || "",
      solution_en: item.solution_en || "",
      cover_image: item.cover_image || "",
      published: item.published ?? true,
      display_order: item.display_order || 0,
    });
    setShowDialog(true);
  };

  const closeDialog = () => {
    setShowDialog(false);
    setEditing(null);
    setForm(BLANK);
  };

  const set = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  /* ---- Styling helpers ---- */
  const inputCls = cn(
    "w-full rounded-lg border px-3 py-2.5 text-sm outline-none transition-colors",
    isDark
      ? "bg-slate-800 border-white/10 text-white placeholder:text-gray-500 focus:border-purple-500"
      : "bg-white border-gray-200 text-gray-900 placeholder:text-gray-400 focus:border-purple-500"
  );

  const labelCls = cn("block text-xs font-semibold mb-1.5", isDark ? "text-gray-400" : "text-gray-500");

  const publishedCount = cases.filter((c) => c.published !== false).length;

  return (
    <div className="max-w-7xl mx-auto" dir={isRTL ? "rtl" : "ltr"}>
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <h1 className={cn("text-3xl font-black", isDark ? "text-white" : "text-gray-900")}>
            {t.title}
          </h1>
          <p className={cn("text-sm mt-1", isDark ? "text-gray-400" : "text-gray-500")}>
            {t.subtitle}
          </p>
        </div>
        <button
          onClick={openNew}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 transition-colors"
        >
          <Plus size={16} /> {t.newCase}
        </button>
      </div>

      {/* Summary chips */}
      <div className="flex flex-wrap gap-3 mb-6">
        <div
          className={cn(
            "inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm",
            isDark ? "bg-slate-800/60 border border-white/10" : "bg-white border border-gray-200 shadow-sm"
          )}
        >
          <Briefcase size={14} className="text-purple-500" />
          <span className={isDark ? "text-gray-400" : "text-gray-500"}>{t.totalCases}:</span>
          <span className={cn("font-bold", isDark ? "text-white" : "text-gray-900")}>{cases.length}</span>
        </div>
        <div
          className={cn(
            "inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm",
            isDark ? "bg-slate-800/60 border border-white/10" : "bg-white border border-gray-200 shadow-sm"
          )}
        >
          <Eye size={14} className="text-green-500" />
          <span className={isDark ? "text-gray-400" : "text-gray-500"}>{t.publishedCount}:</span>
          <span className={cn("font-bold", isDark ? "text-white" : "text-gray-900")}>{publishedCount}</span>
        </div>
      </div>

      {/* Dialog/Modal overlay */}
      {showDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={closeDialog}
          />
          {/* Dialog */}
          <div
            className={cn(
              "relative w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-2xl border p-6",
              isDark
                ? "bg-slate-900 border-white/10"
                : "bg-white border-gray-200 shadow-xl"
            )}
            dir={isRTL ? "rtl" : "ltr"}
          >
            <div className="flex items-center justify-between mb-5">
              <h2 className={cn("text-lg font-bold", isDark ? "text-white" : "text-gray-900")}>
                {editing === "new" ? t.newCase : t.editCase}
              </h2>
              <button
                onClick={closeDialog}
                className={cn(
                  "rounded-lg p-2 transition-colors",
                  isDark ? "text-gray-400 hover:bg-white/10" : "text-gray-400 hover:bg-gray-100"
                )}
              >
                <X size={20} />
              </button>
            </div>

            <div className="space-y-4">
              {/* Titles */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelCls}>{t.titleAr}</label>
                  <input
                    value={form.title_ar}
                    onChange={(e) => set("title_ar", e.target.value)}
                    className={inputCls}
                    dir="rtl"
                  />
                </div>
                <div>
                  <label className={labelCls}>{t.titleEn}</label>
                  <input
                    value={form.title_en}
                    onChange={(e) => set("title_en", e.target.value)}
                    className={inputCls}
                    dir="ltr"
                  />
                </div>
              </div>

              {/* Client, Industry, Cover image, Order */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label className={labelCls}>{t.client}</label>
                  <input
                    value={form.client}
                    onChange={(e) => set("client", e.target.value)}
                    className={inputCls}
                  />
                </div>
                <div>
                  <label className={labelCls}>{t.industry}</label>
                  <input
                    value={form.industry}
                    onChange={(e) => set("industry", e.target.value)}
                    className={inputCls}
                  />
                </div>
                <div>
                  <label className={labelCls}>{t.coverImage}</label>
                  <input
                    value={form.cover_image}
                    onChange={(e) => set("cover_image", e.target.value)}
                    className={inputCls}
                    dir="ltr"
                    placeholder="https://..."
                  />
                </div>
                <div>
                  <label className={labelCls}>{t.displayOrder}</label>
                  <input
                    type="number"
                    value={form.display_order}
                    onChange={(e) => set("display_order", parseInt(e.target.value) || 0)}
                    className={inputCls}
                  />
                </div>
              </div>

              {/* Cover image preview */}
              {form.cover_image && (
                <div className="rounded-lg overflow-hidden">
                  <img
                    src={form.cover_image}
                    alt="Cover preview"
                    className="w-full h-32 object-cover rounded-lg"
                    onError={(e) => {
                      e.target.style.display = "none";
                    }}
                  />
                </div>
              )}

              {/* Challenge */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelCls}>{t.challengeAr}</label>
                  <textarea
                    value={form.challenge_ar}
                    onChange={(e) => set("challenge_ar", e.target.value)}
                    rows={4}
                    className={cn(inputCls, "resize-y")}
                    dir="rtl"
                  />
                </div>
                <div>
                  <label className={labelCls}>{t.challengeEn}</label>
                  <textarea
                    value={form.challenge_en}
                    onChange={(e) => set("challenge_en", e.target.value)}
                    rows={4}
                    className={cn(inputCls, "resize-y")}
                    dir="ltr"
                  />
                </div>
              </div>

              {/* Solution */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelCls}>{t.solutionAr}</label>
                  <textarea
                    value={form.solution_ar}
                    onChange={(e) => set("solution_ar", e.target.value)}
                    rows={4}
                    className={cn(inputCls, "resize-y")}
                    dir="rtl"
                  />
                </div>
                <div>
                  <label className={labelCls}>{t.solutionEn}</label>
                  <textarea
                    value={form.solution_en}
                    onChange={(e) => set("solution_en", e.target.value)}
                    rows={4}
                    className={cn(inputCls, "resize-y")}
                    dir="ltr"
                  />
                </div>
              </div>

              {/* Published toggle */}
              <div className="flex flex-wrap items-center gap-4 pt-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.published}
                    onChange={(e) => set("published", e.target.checked)}
                    className="h-4 w-4 accent-purple-600 rounded"
                  />
                  <span className={cn("text-sm font-semibold", isDark ? "text-gray-300" : "text-gray-600")}>
                    {t.published}
                  </span>
                </label>
              </div>

              {/* Error display */}
              {saveMutation.isError && (
                <div className="rounded-lg bg-red-500/10 border border-red-500/20 px-4 py-2.5 text-sm text-red-400">
                  {saveMutation.error?.message || "Error saving case study"}
                </div>
              )}

              {/* Action buttons */}
              <div className="flex items-center gap-3 pt-2">
                <button
                  onClick={() => saveMutation.mutate()}
                  disabled={saveMutation.isPending}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 transition-colors"
                >
                  {saveMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
                  {saveMutation.isPending ? t.saving : t.save}
                </button>
                <button
                  onClick={closeDialog}
                  className={cn(
                    "px-4 py-2.5 rounded-lg text-sm font-semibold transition-colors",
                    isDark ? "bg-white/10 text-white hover:bg-white/15" : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  )}
                >
                  {t.cancel}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Cases list */}
      {isLoading ? (
        <div className={cn("rounded-xl border p-16 flex justify-center", isDark ? "bg-slate-800/60 border-white/10" : "bg-white border-gray-200")}>
          <Loader2 className="animate-spin text-purple-500" size={28} />
        </div>
      ) : cases.length === 0 ? (
        <div className={cn("rounded-xl border text-center py-16", isDark ? "bg-slate-800/60 border-white/10" : "bg-white border-gray-200")}>
          <Briefcase size={32} className={cn("mx-auto mb-3", isDark ? "text-gray-600" : "text-gray-300")} />
          <p className={cn("text-sm", isDark ? "text-gray-500" : "text-gray-400")}>{t.noResults}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {cases.map((c) => {
            const title = lang === "ar" ? (c.title_ar || c.title_en) : (c.title_en || c.title_ar);
            const challenge = lang === "ar" ? (c.challenge_ar || c.challenge_en) : (c.challenge_en || c.challenge_ar);
            const solution = lang === "ar" ? (c.solution_ar || c.solution_en) : (c.solution_en || c.solution_ar);

            return (
              <div
                key={c.id}
                className={cn(
                  "rounded-xl border overflow-hidden transition-colors",
                  isDark
                    ? "bg-slate-800/60 border-white/10 hover:bg-slate-800/80"
                    : "bg-white border-gray-200 hover:bg-gray-50 shadow-sm"
                )}
              >
                {/* Cover image */}
                {c.cover_image ? (
                  <div className="relative h-36 overflow-hidden">
                    <img
                      src={c.cover_image}
                      alt={title}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.parentElement.style.display = "none";
                      }}
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                    <div className="absolute bottom-3 left-3 right-3">
                      <span className={cn("font-bold text-sm text-white drop-shadow-md")}>
                        {title}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div
                    className={cn(
                      "h-20 flex items-center justify-center",
                      isDark ? "bg-white/5" : "bg-gray-50"
                    )}
                  >
                    <Image size={24} className={isDark ? "text-gray-600" : "text-gray-300"} />
                  </div>
                )}

                {/* Card body */}
                <div className="p-4">
                  {/* Title row (shown if no cover image) */}
                  {!c.cover_image && (
                    <div className="flex flex-wrap items-center gap-2 mb-2">
                      <span className={cn("font-bold text-sm", isDark ? "text-white" : "text-gray-900")}>
                        {title}
                      </span>
                    </div>
                  )}

                  {/* Status and metadata */}
                  <div className="flex flex-wrap items-center gap-2 mb-3">
                    <StatusBadge status={c.published !== false ? "published" : "draft"} lang={lang} />
                    {c.client && (
                      <span className={cn("text-xs px-2 py-0.5 rounded-lg", isDark ? "bg-white/8 text-gray-400" : "bg-gray-100 text-gray-500")}>
                        {t.client}: {c.client}
                      </span>
                    )}
                    {c.industry && (
                      <span className={cn("text-xs px-2 py-0.5 rounded-lg", isDark ? "bg-white/8 text-gray-400" : "bg-gray-100 text-gray-500")}>
                        {t.industry}: {c.industry}
                      </span>
                    )}
                  </div>

                  {/* Challenge & solution snippets */}
                  {challenge && (
                    <div className="mb-2">
                      <span className={cn("text-[10px] font-bold uppercase tracking-wider", isDark ? "text-gray-500" : "text-gray-400")}>
                        {t.challenge}
                      </span>
                      <p className={cn("text-xs mt-0.5 line-clamp-2", isDark ? "text-gray-400" : "text-gray-500")}>
                        {challenge}
                      </p>
                    </div>
                  )}
                  {solution && (
                    <div className="mb-3">
                      <span className={cn("text-[10px] font-bold uppercase tracking-wider", isDark ? "text-gray-500" : "text-gray-400")}>
                        {t.solution}
                      </span>
                      <p className={cn("text-xs mt-0.5 line-clamp-2", isDark ? "text-gray-400" : "text-gray-500")}>
                        {solution}
                      </p>
                    </div>
                  )}

                  {/* Order info */}
                  <div className={cn("text-xs mb-3", isDark ? "text-gray-600" : "text-gray-400")}>
                    {t.order}: {c.display_order ?? 0}
                  </div>

                  {/* Action buttons */}
                  <div className={cn("flex items-center gap-1.5 pt-3 border-t", isDark ? "border-white/5" : "border-gray-100")}>
                    <button
                      onClick={() =>
                        togglePublishMutation.mutate({
                          id: c.id,
                          published: c.published !== false,
                        })
                      }
                      title={c.published !== false ? t.unpublish : t.publish}
                      className={cn(
                        "rounded-lg p-2 transition-colors",
                        c.published !== false
                          ? "text-green-400 hover:bg-green-500/10"
                          : isDark
                          ? "text-gray-500 hover:bg-white/10"
                          : "text-gray-400 hover:bg-gray-100"
                      )}
                    >
                      {c.published !== false ? <Eye size={15} /> : <EyeOff size={15} />}
                    </button>
                    <button
                      onClick={() => openEdit(c)}
                      className="rounded-lg p-2 text-purple-400 hover:bg-purple-500/10 transition-colors"
                    >
                      <Edit size={15} />
                    </button>
                    <button
                      onClick={() => handleDelete(c.id)}
                      disabled={deleteMutation.isPending}
                      className="rounded-lg p-2 text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-40"
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
