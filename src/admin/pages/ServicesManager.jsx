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
  Settings,
} from "lucide-react";

/* ================================================================== */
/*  Bilingual labels                                                   */
/* ================================================================== */
const L = {
  ar: {
    title: "إدارة الخدمات",
    subtitle: "عرض وإدارة جميع الخدمات",
    newService: "خدمة جديدة",
    editService: "تعديل الخدمة",
    titleAr: "العنوان (عربي)",
    titleEn: "العنوان (إنجليزي)",
    slug: "الرابط المختصر",
    descriptionAr: "الوصف (عربي)",
    descriptionEn: "الوصف (إنجليزي)",
    icon: "اسم الأيقونة (Lucide)",
    iconHint: "مثال: Briefcase, Zap, Globe",
    displayOrder: "ترتيب العرض",
    published: "منشور",
    titleLabel: "العنوان",
    order: "الترتيب",
    actions: "إجراءات",
    save: "حفظ",
    saving: "جاري الحفظ...",
    cancel: "إلغاء",
    deleteConfirm: "هل تريد حذف هذه الخدمة؟",
    noResults: "لا توجد خدمات",
    publish: "نشر",
    unpublish: "إلغاء النشر",
    totalServices: "إجمالي الخدمات",
    publishedCount: "منشور",
    description: "الوصف",
  },
  en: {
    title: "Services Manager",
    subtitle: "View and manage all services",
    newService: "New Service",
    editService: "Edit Service",
    titleAr: "Title (Arabic)",
    titleEn: "Title (English)",
    slug: "Slug",
    descriptionAr: "Description (Arabic)",
    descriptionEn: "Description (English)",
    icon: "Icon Name (Lucide)",
    iconHint: "e.g. Briefcase, Zap, Globe",
    displayOrder: "Display Order",
    published: "Published",
    titleLabel: "Title",
    order: "Order",
    actions: "Actions",
    save: "Save",
    saving: "Saving...",
    cancel: "Cancel",
    deleteConfirm: "Are you sure you want to delete this service?",
    noResults: "No services found",
    publish: "Publish",
    unpublish: "Unpublish",
    totalServices: "Total Services",
    publishedCount: "Published",
    description: "Description",
  },
};

/* ================================================================== */
/*  Blank form template                                                */
/* ================================================================== */
const BLANK = {
  title_ar: "",
  title_en: "",
  slug: "",
  description_ar: "",
  description_en: "",
  icon: "",
  display_order: 0,
  published: true,
};

/* ================================================================== */
/*  ServicesManager                                                     */
/* ================================================================== */
export default function ServicesManager() {
  const { lang = "ar", theme = "dark" } = useOutletContext() || {};
  const t = L[lang] || L.ar;
  const isDark = theme === "dark";
  const isRTL = lang === "ar";
  const qc = useQueryClient();

  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(BLANK);
  const [showDialog, setShowDialog] = useState(false);

  /* ---- Fetch services ---- */
  const { data: services = [], isLoading } = useQuery({
    queryKey: ["admin-services"],
    queryFn: () => siteApi.entities.Service.list("display_order", 100),
  });

  /* ---- Mutations ---- */
  const saveMutation = useMutation({
    mutationFn: () => {
      if (editing === "new") {
        return siteApi.entities.Service.create(form);
      }
      return siteApi.entities.Service.update(editing, form);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-services"] });
      closeDialog();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => siteApi.entities.Service.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-services"] }),
  });

  const togglePublishMutation = useMutation({
    mutationFn: ({ id, published }) =>
      siteApi.entities.Service.update(id, { published: !published }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-services"] }),
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
    setForm({ ...BLANK, display_order: services.length });
    setShowDialog(true);
  };

  const openEdit = (item) => {
    setEditing(item.id);
    setForm({
      title_ar: item.title_ar || "",
      title_en: item.title_en || "",
      slug: item.slug || "",
      description_ar: item.description_ar || "",
      description_en: item.description_en || "",
      icon: item.icon || "",
      display_order: item.display_order || 0,
      published: item.published ?? true,
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

  const publishedCount = services.filter((s) => s.published !== false).length;

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
          <Plus size={16} /> {t.newService}
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
          <Settings size={14} className="text-purple-500" />
          <span className={isDark ? "text-gray-400" : "text-gray-500"}>{t.totalServices}:</span>
          <span className={cn("font-bold", isDark ? "text-white" : "text-gray-900")}>{services.length}</span>
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
              "relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl border p-6",
              isDark
                ? "bg-slate-900 border-white/10"
                : "bg-white border-gray-200 shadow-xl"
            )}
            dir={isRTL ? "rtl" : "ltr"}
          >
            <div className="flex items-center justify-between mb-5">
              <h2 className={cn("text-lg font-bold", isDark ? "text-white" : "text-gray-900")}>
                {editing === "new" ? t.newService : t.editService}
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

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className={labelCls}>{t.slug}</label>
                  <input
                    value={form.slug}
                    onChange={(e) => set("slug", e.target.value)}
                    className={inputCls}
                    dir="ltr"
                    placeholder="service-slug"
                  />
                </div>
                <div>
                  <label className={labelCls}>{t.icon}</label>
                  <input
                    value={form.icon}
                    onChange={(e) => set("icon", e.target.value)}
                    className={inputCls}
                    dir="ltr"
                    placeholder={t.iconHint}
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

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelCls}>{t.descriptionAr}</label>
                  <textarea
                    value={form.description_ar}
                    onChange={(e) => set("description_ar", e.target.value)}
                    rows={5}
                    className={cn(inputCls, "resize-y")}
                    dir="rtl"
                  />
                </div>
                <div>
                  <label className={labelCls}>{t.descriptionEn}</label>
                  <textarea
                    value={form.description_en}
                    onChange={(e) => set("description_en", e.target.value)}
                    rows={5}
                    className={cn(inputCls, "resize-y")}
                    dir="ltr"
                  />
                </div>
              </div>

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

              {saveMutation.isError && (
                <div className="rounded-lg bg-red-500/10 border border-red-500/20 px-4 py-2.5 text-sm text-red-400">
                  {saveMutation.error?.message || "Error saving service"}
                </div>
              )}

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

      {/* Services list */}
      {isLoading ? (
        <div className={cn("rounded-xl border p-16 flex justify-center", isDark ? "bg-slate-800/60 border-white/10" : "bg-white border-gray-200")}>
          <Loader2 className="animate-spin text-purple-500" size={28} />
        </div>
      ) : services.length === 0 ? (
        <div className={cn("rounded-xl border text-center py-16", isDark ? "bg-slate-800/60 border-white/10" : "bg-white border-gray-200")}>
          <Settings size={32} className={cn("mx-auto mb-3", isDark ? "text-gray-600" : "text-gray-300")} />
          <p className={cn("text-sm", isDark ? "text-gray-500" : "text-gray-400")}>{t.noResults}</p>
        </div>
      ) : (
        <div className="space-y-3">
          {services.map((svc) => {
            const title = lang === "ar" ? (svc.title_ar || svc.title_en) : (svc.title_en || svc.title_ar);
            const desc = lang === "ar" ? (svc.description_ar || svc.description_en) : (svc.description_en || svc.description_ar);

            return (
              <div
                key={svc.id}
                className={cn(
                  "rounded-xl border p-4 transition-colors",
                  isDark
                    ? "bg-slate-800/60 border-white/10 hover:bg-slate-800/80"
                    : "bg-white border-gray-200 hover:bg-gray-50 shadow-sm"
                )}
              >
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      {svc.icon && (
                        <span
                          className={cn(
                            "inline-flex items-center justify-center w-8 h-8 rounded-lg text-xs font-bold",
                            isDark ? "bg-purple-500/15 text-purple-400" : "bg-purple-50 text-purple-600"
                          )}
                        >
                          {svc.icon.slice(0, 2)}
                        </span>
                      )}
                      <span className={cn("font-bold text-sm", isDark ? "text-white" : "text-gray-900")}>
                        {title}
                      </span>
                      <StatusBadge status={svc.published !== false ? "published" : "draft"} lang={lang} />
                    </div>
                    {desc && (
                      <p className={cn("text-xs mt-1 line-clamp-2", isDark ? "text-gray-400" : "text-gray-500")}>
                        {desc}
                      </p>
                    )}
                    <div className={cn("text-xs flex flex-wrap gap-3 mt-1.5", isDark ? "text-gray-500" : "text-gray-400")}>
                      {svc.slug && <span>/{svc.slug}</span>}
                      <span>{t.order}: {svc.display_order ?? 0}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 flex-shrink-0">
                    <button
                      onClick={() =>
                        togglePublishMutation.mutate({
                          id: svc.id,
                          published: svc.published !== false,
                        })
                      }
                      title={svc.published !== false ? t.unpublish : t.publish}
                      className={cn(
                        "rounded-lg p-2 transition-colors",
                        svc.published !== false
                          ? "text-green-400 hover:bg-green-500/10"
                          : isDark
                          ? "text-gray-500 hover:bg-white/10"
                          : "text-gray-400 hover:bg-gray-100"
                      )}
                    >
                      {svc.published !== false ? <Eye size={15} /> : <EyeOff size={15} />}
                    </button>
                    <button
                      onClick={() => openEdit(svc)}
                      className="rounded-lg p-2 text-purple-400 hover:bg-purple-500/10 transition-colors"
                    >
                      <Edit size={15} />
                    </button>
                    <button
                      onClick={() => handleDelete(svc.id)}
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
