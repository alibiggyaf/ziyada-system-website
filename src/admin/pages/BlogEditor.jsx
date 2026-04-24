import { useState, useEffect } from "react";
import { useOutletContext, useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { siteApi } from "@/api/siteApi";
import { cn } from "@/lib/utils";
import { Save, ArrowLeft, ArrowRight, Loader2, Image, Eye, EyeOff } from "lucide-react";
import ReactMarkdown from "react-markdown";

/* ================================================================== */
/*  Bilingual labels                                                   */
/* ================================================================== */
const L = {
  ar: {
    title: "محرر المقالات",
    newPost: "مقال جديد",
    editPost: "تعديل المقال",
    titleAr: "العنوان (عربي)",
    titleEn: "العنوان (إنجليزي)",
    slug: "الرابط المختصر (Slug)",
    excerptAr: "المقتطف (عربي)",
    excerptEn: "المقتطف (إنجليزي)",
    contentAr: "المحتوى (عربي - Markdown)",
    contentEn: "المحتوى (إنجليزي - Markdown)",
    category: "التصنيف",
    tags: "الوسوم (مفصولة بفواصل)",
    author: "الكاتب",
    coverImage: "رابط صورة الغلاف",
    seoTitle: "عنوان SEO",
    metaDescription: "وصف ميتا",
    published: "منشور",
    save: "حفظ",
    saving: "جاري الحفظ...",
    back: "رجوع",
    preview: "معاينة",
    form: "النموذج",
    previewLang: "لغة المعاينة",
    saveError: "حدث خطأ أثناء الحفظ",
    contentPlaceholder: "المحتوى سيظهر هنا...",
    titlePlaceholder: "عنوان المقال",
    metaFields: "حقول SEO",
    mainFields: "المحتوى الأساسي",
    mediaFields: "الوسائط والتصنيف",
  },
  en: {
    title: "Blog Editor",
    newPost: "New Post",
    editPost: "Edit Post",
    titleAr: "Title (Arabic)",
    titleEn: "Title (English)",
    slug: "Slug",
    excerptAr: "Excerpt (Arabic)",
    excerptEn: "Excerpt (English)",
    contentAr: "Content (Arabic - Markdown)",
    contentEn: "Content (English - Markdown)",
    category: "Category",
    tags: "Tags (comma-separated)",
    author: "Author",
    coverImage: "Cover Image URL",
    seoTitle: "SEO Title",
    metaDescription: "Meta Description",
    published: "Published",
    save: "Save",
    saving: "Saving...",
    back: "Back",
    preview: "Preview",
    form: "Form",
    previewLang: "Preview Language",
    saveError: "Error saving post",
    contentPlaceholder: "Content preview will appear here...",
    titlePlaceholder: "Post Title",
    metaFields: "SEO Fields",
    mainFields: "Main Content",
    mediaFields: "Media & Category",
  },
};

/* ================================================================== */
/*  Blank form template                                                */
/* ================================================================== */
const BLANK_FORM = {
  title_ar: "",
  title_en: "",
  slug: "",
  excerpt_ar: "",
  excerpt_en: "",
  content_ar: "",
  content_en: "",
  category: "",
  tags: "",
  author: "Ziyada",
  cover_image: "",
  seo_title: "",
  meta_description: "",
  published: false,
};

/* ================================================================== */
/*  Slug generator                                                     */
/* ================================================================== */
function generateSlug(title) {
  return title
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

/* ================================================================== */
/*  BlogEditor                                                         */
/* ================================================================== */
export default function BlogEditor() {
  const { lang = "ar", theme = "dark" } = useOutletContext() || {};
  const t = L[lang] || L.ar;
  const isDark = theme === "dark";
  const isRTL = lang === "ar";
  const { id } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const isEditing = Boolean(id);

  const [form, setForm] = useState(BLANK_FORM);
  const [previewLang, setPreviewLang] = useState(lang);
  const [autoSlug, setAutoSlug] = useState(true);

  /* ---- Load existing post ---- */
  const { data: existingPost, isLoading: loadingPost } = useQuery({
    queryKey: ["admin-post", id],
    queryFn: () => siteApi.entities.BlogPost.get(id),
    enabled: isEditing,
  });

  useEffect(() => {
    if (existingPost) {
      setForm({
        title_ar: existingPost.title_ar || "",
        title_en: existingPost.title_en || "",
        slug: existingPost.slug || "",
        excerpt_ar: existingPost.excerpt_ar || "",
        excerpt_en: existingPost.excerpt_en || "",
        content_ar: existingPost.content_ar || "",
        content_en: existingPost.content_en || "",
        category: existingPost.category || "",
        tags: Array.isArray(existingPost.tags)
          ? existingPost.tags.join(", ")
          : existingPost.tags || "",
        author: existingPost.author || "Ziyada",
        cover_image: existingPost.cover_image || "",
        seo_title: existingPost.seo_title || "",
        meta_description: existingPost.meta_description || "",
        published: existingPost.published || false,
      });
      setAutoSlug(false);
    }
  }, [existingPost]);

  /* ---- Auto-generate slug from title_en ---- */
  useEffect(() => {
    if (autoSlug && form.title_en) {
      setForm((prev) => ({ ...prev, slug: generateSlug(prev.title_en) }));
    }
  }, [form.title_en, autoSlug]);

  /* ---- Field setter ---- */
  const set = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    if (key === "slug") setAutoSlug(false);
  };

  /* ---- Save mutation ---- */
  const saveMutation = useMutation({
    mutationFn: () => {
      const payload = {
        ...form,
        tags: form.tags
          ? form.tags
              .split(",")
              .map((tag) => tag.trim())
              .filter(Boolean)
          : [],
        status: form.published ? "published" : "draft",
      };
      if (isEditing) {
        return siteApi.entities.BlogPost.update(id, payload);
      }
      return siteApi.entities.BlogPost.create(payload);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-posts"] });
      navigate("/admin/blog");
    },
  });

  /* ---- Styling helpers ---- */
  const inputCls = cn(
    "w-full rounded-lg border px-3 py-2.5 text-sm outline-none transition-colors",
    isDark
      ? "bg-slate-800 border-white/10 text-white placeholder:text-gray-500 focus:border-purple-500"
      : "bg-white border-gray-200 text-gray-900 placeholder:text-gray-400 focus:border-purple-500"
  );

  const textareaCls = cn(inputCls, "resize-y");

  const labelCls = cn("block text-xs font-semibold mb-1.5", isDark ? "text-gray-400" : "text-gray-500");

  const sectionCls = cn(
    "rounded-xl border p-5",
    isDark ? "bg-slate-800/60 border-white/10" : "bg-white border-gray-200 shadow-sm"
  );

  const sectionTitleCls = cn(
    "text-sm font-bold mb-4 pb-2 border-b",
    isDark ? "text-gray-300 border-white/10" : "text-gray-700 border-gray-100"
  );

  /* ---- Preview data ---- */
  const previewContent = previewLang === "ar" ? form.content_ar : form.content_en;
  const previewTitle = previewLang === "ar" ? form.title_ar : form.title_en;
  const previewExcerpt = previewLang === "ar" ? form.excerpt_ar : form.excerpt_en;

  /* ---- Loading state ---- */
  if (isEditing && loadingPost) {
    return (
      <div className="flex justify-center items-center py-32">
        <Loader2 className="animate-spin text-purple-500" size={32} />
      </div>
    );
  }

  return (
    <div className="max-w-[1400px] mx-auto" dir={isRTL ? "rtl" : "ltr"}>
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate("/admin/blog")}
            className={cn(
              "rounded-lg p-2 transition-colors",
              isDark ? "hover:bg-white/10 text-gray-400" : "hover:bg-gray-100 text-gray-500"
            )}
          >
            {isRTL ? <ArrowRight size={20} /> : <ArrowLeft size={20} />}
          </button>
          <div>
            <h1 className={cn("text-2xl font-black", isDark ? "text-white" : "text-gray-900")}>
              {isEditing ? t.editPost : t.newPost}
            </h1>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {/* Published toggle */}
          <button
            onClick={() => set("published", !form.published)}
            className={cn(
              "inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold transition-colors border",
              form.published
                ? isDark
                  ? "bg-green-500/10 border-green-500/30 text-green-400"
                  : "bg-green-50 border-green-200 text-green-700"
                : isDark
                ? "bg-white/5 border-white/10 text-gray-400"
                : "bg-gray-50 border-gray-200 text-gray-500"
            )}
          >
            {form.published ? <Eye size={15} /> : <EyeOff size={15} />}
            {form.published ? t.published : "Draft"}
          </button>
          {/* Save button */}
          <button
            onClick={() => saveMutation.mutate()}
            disabled={saveMutation.isPending}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 transition-colors disabled:opacity-50"
          >
            {saveMutation.isPending ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Save size={16} />
            )}
            {saveMutation.isPending ? t.saving : t.save}
          </button>
        </div>
      </div>

      {/* Error message */}
      {saveMutation.isError && (
        <div className="mb-4 rounded-lg bg-red-500/10 border border-red-500/20 px-4 py-3 text-sm text-red-400">
          {saveMutation.error?.message || t.saveError}
        </div>
      )}

      {/* Two-column layout: 60% form / 40% preview */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Left: Form (3/5 = 60%) */}
        <div className="lg:col-span-3 space-y-5">
          {/* Main content section */}
          <div className={sectionCls}>
            <h3 className={sectionTitleCls}>{t.mainFields}</h3>
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

              <div>
                <label className={labelCls}>{t.slug}</label>
                <input
                  value={form.slug}
                  onChange={(e) => set("slug", e.target.value)}
                  className={inputCls}
                  dir="ltr"
                  placeholder="auto-generated-from-title"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelCls}>{t.excerptAr}</label>
                  <textarea
                    value={form.excerpt_ar}
                    onChange={(e) => set("excerpt_ar", e.target.value)}
                    rows={3}
                    className={textareaCls}
                    dir="rtl"
                  />
                </div>
                <div>
                  <label className={labelCls}>{t.excerptEn}</label>
                  <textarea
                    value={form.excerpt_en}
                    onChange={(e) => set("excerpt_en", e.target.value)}
                    rows={3}
                    className={textareaCls}
                    dir="ltr"
                  />
                </div>
              </div>

              <div>
                <label className={labelCls}>{t.contentAr}</label>
                <textarea
                  value={form.content_ar}
                  onChange={(e) => set("content_ar", e.target.value)}
                  rows={12}
                  className={textareaCls}
                  dir="rtl"
                />
              </div>

              <div>
                <label className={labelCls}>{t.contentEn}</label>
                <textarea
                  value={form.content_en}
                  onChange={(e) => set("content_en", e.target.value)}
                  rows={12}
                  className={textareaCls}
                  dir="ltr"
                />
              </div>
            </div>
          </div>

          {/* Media & Category section */}
          <div className={sectionCls}>
            <h3 className={sectionTitleCls}>{t.mediaFields}</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelCls}>{t.category}</label>
                  <input
                    value={form.category}
                    onChange={(e) => set("category", e.target.value)}
                    className={inputCls}
                  />
                </div>
                <div>
                  <label className={labelCls}>{t.tags}</label>
                  <input
                    value={form.tags}
                    onChange={(e) => set("tags", e.target.value)}
                    className={inputCls}
                    placeholder="tag1, tag2, tag3"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelCls}>{t.author}</label>
                  <input
                    value={form.author}
                    onChange={(e) => set("author", e.target.value)}
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
              </div>
            </div>
          </div>

          {/* SEO section */}
          <div className={sectionCls}>
            <h3 className={sectionTitleCls}>{t.metaFields}</h3>
            <div className="space-y-4">
              <div>
                <label className={labelCls}>{t.seoTitle}</label>
                <input
                  value={form.seo_title}
                  onChange={(e) => set("seo_title", e.target.value)}
                  className={inputCls}
                />
              </div>
              <div>
                <label className={labelCls}>{t.metaDescription}</label>
                <textarea
                  value={form.meta_description}
                  onChange={(e) => set("meta_description", e.target.value)}
                  rows={3}
                  className={textareaCls}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Right: Preview (2/5 = 40%) */}
        <div className="lg:col-span-2">
          <div className="sticky top-4">
            {/* Preview header */}
            <div className="flex items-center justify-between mb-3">
              <h2 className={cn("text-lg font-bold", isDark ? "text-white" : "text-gray-900")}>
                {t.preview}
              </h2>
              <div className="flex gap-1.5">
                <button
                  onClick={() => setPreviewLang("ar")}
                  className={cn(
                    "px-3 py-1 rounded-lg text-xs font-semibold transition-colors",
                    previewLang === "ar"
                      ? "bg-purple-600 text-white"
                      : isDark
                      ? "bg-white/8 text-gray-400 hover:bg-white/12"
                      : "bg-gray-100 text-gray-500 hover:bg-gray-200"
                  )}
                >
                  AR
                </button>
                <button
                  onClick={() => setPreviewLang("en")}
                  className={cn(
                    "px-3 py-1 rounded-lg text-xs font-semibold transition-colors",
                    previewLang === "en"
                      ? "bg-purple-600 text-white"
                      : isDark
                      ? "bg-white/8 text-gray-400 hover:bg-white/12"
                      : "bg-gray-100 text-gray-500 hover:bg-gray-200"
                  )}
                >
                  EN
                </button>
              </div>
            </div>

            {/* Preview panel */}
            <div
              className={cn(
                "rounded-xl border p-6 min-h-[600px] max-h-[calc(100vh-200px)] overflow-y-auto",
                isDark ? "bg-slate-800/60 border-white/10" : "bg-white border-gray-200 shadow-sm"
              )}
              dir={previewLang === "ar" ? "rtl" : "ltr"}
            >
              {/* Cover image preview */}
              {form.cover_image ? (
                <img
                  src={form.cover_image}
                  alt="Cover"
                  className="w-full h-48 object-cover rounded-lg mb-6"
                  onError={(e) => {
                    e.target.style.display = "none";
                  }}
                />
              ) : (
                <div
                  className={cn(
                    "w-full h-48 rounded-lg mb-6 flex items-center justify-center",
                    isDark ? "bg-white/5" : "bg-gray-100"
                  )}
                >
                  <Image size={32} className={isDark ? "text-gray-600" : "text-gray-300"} />
                </div>
              )}

              {/* Category & Tags */}
              {(form.category || form.tags) && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {form.category && (
                    <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-purple-500/15 text-purple-400 border border-purple-500/30">
                      {form.category}
                    </span>
                  )}
                  {form.tags &&
                    form.tags
                      .split(",")
                      .map((tag) => tag.trim())
                      .filter(Boolean)
                      .map((tag, i) => (
                        <span
                          key={i}
                          className={cn(
                            "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
                            isDark ? "bg-white/8 text-gray-400" : "bg-gray-100 text-gray-500"
                          )}
                        >
                          {tag}
                        </span>
                      ))}
                </div>
              )}

              {/* Title */}
              <h1
                className={cn(
                  "text-2xl font-black mb-3 leading-tight",
                  isDark ? "text-white" : "text-gray-900"
                )}
              >
                {previewTitle || t.titlePlaceholder}
              </h1>

              {/* Author & date */}
              <div className={cn("flex items-center gap-3 mb-4 text-xs", isDark ? "text-gray-500" : "text-gray-400")}>
                {form.author && <span>{form.author}</span>}
                <span>{new Date().toLocaleDateString(previewLang === "ar" ? "ar-SA" : "en-US")}</span>
              </div>

              {/* Excerpt */}
              {previewExcerpt && (
                <p
                  className={cn(
                    "text-sm mb-6 leading-relaxed italic border-l-4 pl-4",
                    isDark
                      ? "text-gray-400 border-purple-500/40"
                      : "text-gray-500 border-purple-300"
                  )}
                >
                  {previewExcerpt}
                </p>
              )}

              {/* Markdown content */}
              <div
                className={cn(
                  "prose max-w-none text-sm leading-relaxed",
                  isDark ? "prose-invert" : ""
                )}
              >
                {previewContent ? (
                  <ReactMarkdown>{previewContent}</ReactMarkdown>
                ) : (
                  <p className={isDark ? "text-gray-600" : "text-gray-300"}>
                    {t.contentPlaceholder}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
