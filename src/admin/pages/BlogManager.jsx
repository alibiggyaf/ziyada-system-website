import { useState, useMemo, useCallback } from "react";
import { useOutletContext, Link, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { siteApi } from "@/api/siteApi";
import { cn } from "@/lib/utils";
import DataTable from "@/admin/components/DataTable";
import StatusBadge from "@/admin/components/StatusBadge";
import {
  Plus,
  Edit,
  Trash2,
  Eye,
  EyeOff,
  Search,
  Loader2,
  FileText,
} from "lucide-react";
import { format } from "date-fns";

/* ================================================================== */
/*  Bilingual labels                                                   */
/* ================================================================== */
const L = {
  ar: {
    title: "إدارة المدونة",
    subtitle: "أنشئ المحتوى، راجعه، ثم انشره أو احتفظ به كمسودة",
    newPost: "مقال جديد",
    titleCol: "العنوان",
    status: "الحالة",
    category: "التصنيف",
    author: "الكاتب",
    publishedDate: "تاريخ النشر",
    actions: "إجراءات",
    published: "منشور",
    draft: "مسودة",
    all: "الكل",
    deleteConfirm: "هل تريد حذف هذا المقال؟",
    noResults: "لا توجد مقالات مطابقة. غيّر الفلتر أو كلمة البحث.",
    publish: "نشر",
    unpublish: "إلغاء النشر",
    search: "بحث في المقالات...",
    totalPosts: "إجمالي المقالات",
    publishedCount: "منشور",
    draftCount: "مسودة",
    newPostHint: "فتح صفحة إنشاء مقال جديد.",
    publishHint: "تغيير حالة المقال بين منشور ومسودة.",
    editHint: "فتح المقال لتعديله.",
    deleteHint: "حذف المقال نهائيًا من الإدارة.",
  },
  en: {
    title: "Blog Manager",
    subtitle: "Create content, review it, and publish or keep as draft",
    newPost: "New Post",
    titleCol: "Title",
    status: "Status",
    category: "Category",
    author: "Author",
    publishedDate: "Published Date",
    actions: "Actions",
    published: "Published",
    draft: "Draft",
    all: "All",
    deleteConfirm: "Are you sure you want to delete this post?",
    noResults: "No matching posts. Try another filter or search term.",
    publish: "Publish",
    unpublish: "Unpublish",
    search: "Search posts...",
    totalPosts: "Total Posts",
    publishedCount: "Published",
    draftCount: "Draft",
    newPostHint: "Open the page to create a new blog post.",
    publishHint: "Toggle this post between published and draft.",
    editHint: "Open this post in the editor.",
    deleteHint: "Permanently delete this post from admin.",
  },
};

/* ================================================================== */
/*  BlogManager                                                        */
/* ================================================================== */
export default function BlogManager() {
  const { lang = "ar", theme = "dark" } = useOutletContext() || {};
  const t = L[lang] || L.ar;
  const isDark = theme === "dark";
  const isRTL = lang === "ar";
  const navigate = useNavigate();
  const qc = useQueryClient();

  /* ---- Local state ---- */
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  /* ---- Fetch posts ---- */
  const { data: posts = [], isLoading } = useQuery({
    queryKey: ["admin-posts"],
    queryFn: () => siteApi.entities.BlogPost.list("-created_at", 500),
  });

  /* ---- Mutations ---- */
  const togglePublishMutation = useMutation({
    mutationFn: ({ id, published }) =>
      siteApi.entities.BlogPost.update(id, {
        published: !published,
        status: !published ? "published" : "draft",
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-posts"] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => siteApi.entities.BlogPost.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-posts"] }),
  });

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
    return posts.filter((post) => {
      if (statusFilter === "published" && !post.published) return false;
      if (statusFilter === "draft" && post.published) return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const titleAr = (post.title_ar || "").toLowerCase();
        const titleEn = (post.title_en || "").toLowerCase();
        const cat = (post.category || "").toLowerCase();
        const author = (post.author || "").toLowerCase();
        if (!titleAr.includes(q) && !titleEn.includes(q) && !cat.includes(q) && !author.includes(q)) {
          return false;
        }
      }
      return true;
    });
  }, [posts, statusFilter, searchQuery]);

  /* ---- Stats ---- */
  const publishedCount = posts.filter((p) => p.published).length;
  const draftCount = posts.filter((p) => !p.published).length;

  /* ---- Table columns ---- */
  const columns = [
    {
      key: "title",
      label: t.titleCol,
      render: (_, r) => (
        <div className="min-w-[200px]">
          <div className={cn("font-semibold text-sm", isDark ? "text-white" : "text-gray-900")}>
            {lang === "ar" ? (r.title_ar || r.title_en) : (r.title_en || r.title_ar)}
          </div>
          {r.slug && (
            <div className={cn("text-xs mt-0.5", isDark ? "text-gray-500" : "text-gray-400")}>
              /{r.slug}
            </div>
          )}
        </div>
      ),
    },
    {
      key: "status",
      label: t.status,
      render: (_, r) => (
        <StatusBadge status={r.published ? "published" : "draft"} lang={lang} />
      ),
    },
    {
      key: "category",
      label: t.category,
      render: (_, r) =>
        r.category ? (
          <span
            className={cn(
              "inline-flex items-center rounded-lg px-2.5 py-0.5 text-xs font-medium",
              isDark ? "bg-white/8 text-gray-300" : "bg-gray-100 text-gray-600"
            )}
          >
            {r.category}
          </span>
        ) : (
          <span className={isDark ? "text-gray-600" : "text-gray-300"}>{"\u2014"}</span>
        ),
    },
    {
      key: "author",
      label: t.author,
      render: (_, r) => (
        <span className={cn("text-sm", isDark ? "text-gray-300" : "text-gray-600")}>
          {r.author || "\u2014"}
        </span>
      ),
    },
    {
      key: "published_date",
      label: t.publishedDate,
      render: (_, r) => {
        try {
          const d = r.published_date || r.created_at;
          return d ? (
            <span className={cn("text-sm", isDark ? "text-gray-400" : "text-gray-500")}>
              {format(new Date(d), "yyyy-MM-dd")}
            </span>
          ) : "\u2014";
        } catch {
          return "\u2014";
        }
      },
    },
    {
      key: "actions",
      label: t.actions,
      render: (_, r) => (
        <div className="flex items-center gap-1">
          <button
            onClick={(e) => {
              e.stopPropagation();
              togglePublishMutation.mutate({ id: r.id, published: r.published });
            }}
            title={`${r.published ? t.unpublish : t.publish} - ${t.publishHint}`}
            className={cn(
              "rounded-lg p-2 transition-colors",
              r.published
                ? "text-green-400 hover:bg-green-500/10"
                : isDark
                ? "text-gray-500 hover:bg-white/10"
                : "text-gray-400 hover:bg-gray-100"
            )}
          >
            {r.published ? <Eye size={15} /> : <EyeOff size={15} />}
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/admin/blog/edit/${r.id}`);
            }}
            title={t.editHint}
            className="rounded-lg p-2 text-purple-400 hover:bg-purple-500/10 transition-colors"
          >
            <Edit size={15} />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleDelete(r.id);
            }}
            disabled={deleteMutation.isPending}
            title={t.deleteHint}
            className="rounded-lg p-2 text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-40"
          >
            <Trash2 size={15} />
          </button>
        </div>
      ),
    },
  ];

  const statusOptions = ["all", "published", "draft"];

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
        <Link
          to="/admin/blog/new"
          title={t.newPostHint}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 transition-colors"
        >
          <Plus size={16} /> {t.newPost}
        </Link>
      </div>

      {/* Summary chips */}
      <div className="flex flex-wrap gap-3 mb-6">
        <div
          className={cn(
            "inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm",
            isDark ? "bg-slate-800/60 border border-white/10" : "bg-white border border-gray-200 shadow-sm"
          )}
        >
          <FileText size={14} className="text-purple-500" />
          <span className={isDark ? "text-gray-400" : "text-gray-500"}>{t.totalPosts}:</span>
          <span className={cn("font-bold", isDark ? "text-white" : "text-gray-900")}>{posts.length}</span>
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
        <div
          className={cn(
            "inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm",
            isDark ? "bg-slate-800/60 border border-white/10" : "bg-white border border-gray-200 shadow-sm"
          )}
        >
          <EyeOff size={14} className="text-gray-400" />
          <span className={isDark ? "text-gray-400" : "text-gray-500"}>{t.draftCount}:</span>
          <span className={cn("font-bold", isDark ? "text-white" : "text-gray-900")}>{draftCount}</span>
        </div>
      </div>

      {/* Filter bar */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
        {/* Status filter */}
        <div className="flex flex-wrap gap-1.5">
          {statusOptions.map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              title={t.status}
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

        <div className={cn("w-px h-6", isDark ? "bg-white/10" : "bg-gray-200")} />

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
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t.search}
              title={t.search}
              className={cn(
                "w-full rounded-lg border text-sm py-2 outline-none transition-colors",
                isRTL ? "pr-9 pl-3" : "pl-9 pr-3",
                isDark
                  ? "bg-slate-800 border-white/10 text-white placeholder:text-gray-500 focus:border-purple-500"
                  : "bg-white border-gray-200 text-gray-900 placeholder:text-gray-400 focus:border-purple-500"
              )}
            />
          </div>
        </div>
      </div>

      {/* Table */}
      {isLoading ? (
        <div
          className={cn(
            "rounded-xl border p-16 flex justify-center",
            isDark ? "bg-slate-800/60 border-white/10" : "bg-white border-gray-200"
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
