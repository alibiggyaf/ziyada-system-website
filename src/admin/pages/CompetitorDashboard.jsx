import { useState, useMemo } from "react";
import { useOutletContext, useNavigate, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/lib/supabase";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { formatDistanceToNow } from "date-fns";
import StatCard from "@/admin/components/StatCard";
import {
  Globe,
  Instagram,
  Youtube,
  Music2,
  Clock,
  RefreshCw,
  Loader2,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  CheckCircle2,
  XCircle,
  PencilLine,
  Sparkles,
  Database,
  FileText,
  TrendingUp,
  Hash,
  Users,
  Linkedin,
  Image,
  LayoutGrid,
  Video,
  Zap,
} from "lucide-react";

/* ================================================================== */
/*  Bilingual labels                                                   */
/* ================================================================== */
const L = {
  ar: {
    competitorDashboard: "استخبارات المنافسين",
    subtitle: "تحليل محتوى ثمانية وتوليد أفكار لزيادة",
    thmanyahContent: "محتوى ثمانية",
    contentSuggestions: "اقتراحات المحتوى",
    scrapeNow: "رصد الآن",
    totalIntel: "إجمالي التحليلات",
    pendingSuggestions: "اقتراحات معلقة",
    approvedPublished: "معتمد/منشور",
    lastScraped: "آخر رصد",
    generateContent: "توليد محتوى",
    approveBlogDraft: "اعتماد → مسودة مدونة",
    reject: "رفض",
    hooks: "الخطافات التسويقية",
    imagePrompt: "بروميت الصورة",
    carouselPrompt: "بروميت الكاروسيل",
    videoPrompt: "بروميت الفيديو",
    animationPrompt: "بروميت الحركة",
    copy: "نسخ",
    copied: "تم النسخ!",
    noIntelYet: "لا توجد تحليلات بعد. اضغط «رصد الآن» لبدء الرصد.",
    noSuggestionsYet: "لا توجد اقتراحات بعد. أنشئ محتوى من بيانات ثمانية.",
    website: "الموقع",
    instagram: "إنستقرام",
    tiktok: "تيك توك",
    youtube: "يوتيوب",
    all: "الكل",
    pending: "معلق",
    approved: "معتمد",
    rejected: "مرفوض",
    published: "منشور",
    blog: "مدونة",
    facebook: "فيسبوك",
    linkedin: "لينكدإن",
    showMore: "عرض المزيد",
    showLess: "عرض أقل",
    engagement: "التفاعل",
    editInBlog: "تعديل في المدونة",
    neverScraped: "لم يتم الرصد بعد",
    creativePrompts: "البروميتات الإبداعية",
    scraping: "جارٍ الرصد...",
    generating: "جارٍ التوليد...",
    approving: "جارٍ الاعتماد...",
    platform: "المنصة",
    status: "الحالة",
    noResults: "لا توجد نتائج",
  },
  en: {
    competitorDashboard: "Competitor Intel",
    subtitle: "Analyzing Thmanyah content & generating ideas for Ziyada",
    thmanyahContent: "Thmanyah Content",
    contentSuggestions: "Content Suggestions",
    scrapeNow: "Scrape Now",
    totalIntel: "Total Intel",
    pendingSuggestions: "Pending Suggestions",
    approvedPublished: "Approved/Published",
    lastScraped: "Last Scraped",
    generateContent: "Generate Content",
    approveBlogDraft: "Approve → Blog Draft",
    reject: "Reject",
    hooks: "Hooks",
    imagePrompt: "Image Prompt",
    carouselPrompt: "Carousel Prompt",
    videoPrompt: "Video Prompt",
    animationPrompt: "Animation Prompt",
    copy: "Copy",
    copied: "Copied!",
    noIntelYet: 'No intel yet. Click "Scrape Now" to start.',
    noSuggestionsYet: "No suggestions yet. Generate content from Thmanyah intel.",
    website: "Website",
    instagram: "Instagram",
    tiktok: "TikTok",
    youtube: "YouTube",
    all: "All",
    pending: "Pending",
    approved: "Approved",
    rejected: "Rejected",
    published: "Published",
    blog: "Blog",
    facebook: "Facebook",
    linkedin: "LinkedIn",
    showMore: "Show more",
    showLess: "Show less",
    engagement: "Engagement",
    editInBlog: "Edit in Blog",
    neverScraped: "Never scraped",
    creativePrompts: "Creative Prompts",
    scraping: "Scraping...",
    generating: "Generating...",
    approving: "Approving...",
    platform: "Platform",
    status: "Status",
    noResults: "No results",
  },
};

/* ================================================================== */
/*  Badge config                                                        */
/* ================================================================== */
const SOURCE_CFG = {
  website:   { Icon: Globe,     dark: "bg-blue-500/15 text-blue-400",     light: "bg-blue-100 text-blue-600" },
  instagram: { Icon: Instagram, dark: "bg-pink-500/15 text-pink-400",     light: "bg-pink-100 text-pink-600" },
  tiktok:    { Icon: Music2,    dark: "bg-slate-600/30 text-slate-300",   light: "bg-slate-100 text-slate-600" },
  youtube:   { Icon: Youtube,   dark: "bg-red-500/15 text-red-400",       light: "bg-red-100 text-red-600" },
};

const PLATFORM_CFG = {
  blog:      { Icon: FileText,   dark: "bg-purple-500/15 text-purple-400", light: "bg-purple-100 text-purple-600" },
  tiktok:    { Icon: Music2,     dark: "bg-slate-700 text-slate-100",      light: "bg-slate-200 text-slate-800" },
  instagram: { Icon: Instagram,  dark: "bg-pink-500/15 text-pink-400",     light: "bg-pink-100 text-pink-600" },
  facebook:  { Icon: Users,      dark: "bg-blue-600/15 text-blue-400",     light: "bg-blue-100 text-blue-600" },
  linkedin:  { Icon: Linkedin,   dark: "bg-sky-500/15 text-sky-400",       light: "bg-sky-100 text-sky-600" },
};

const STATUS_CFG = {
  pending:   { dark: "bg-yellow-500/15 text-yellow-400",   light: "bg-yellow-100 text-yellow-700" },
  approved:  { dark: "bg-green-500/15 text-green-400",     light: "bg-green-100 text-green-700" },
  rejected:  { dark: "bg-red-500/15 text-red-400",         light: "bg-red-100 text-red-700" },
  published: { dark: "bg-emerald-500/15 text-emerald-400", light: "bg-emerald-100 text-emerald-700" },
};

/* ================================================================== */
/*  SkeletonCard                                                        */
/* ================================================================== */
function SkeletonCard({ isDark }) {
  return (
    <div
      className={cn(
        "rounded-xl border p-5 animate-pulse",
        isDark ? "bg-slate-800 border-slate-700" : "bg-white border-gray-200"
      )}
    >
      <div className="flex items-center justify-between gap-2 mb-4">
        <div className={cn("h-5 w-20 rounded-full", isDark ? "bg-slate-700" : "bg-gray-200")} />
        <div className={cn("h-4 w-12 rounded", isDark ? "bg-slate-700" : "bg-gray-200")} />
      </div>
      <div className={cn("h-5 w-3/4 rounded mb-2", isDark ? "bg-slate-700" : "bg-gray-200")} />
      <div className={cn("h-4 w-1/2 rounded mb-4", isDark ? "bg-slate-700" : "bg-gray-200")} />
      <div className={cn("h-14 w-full rounded mb-5", isDark ? "bg-slate-700" : "bg-gray-200")} />
      <div className="flex gap-2">
        <div className={cn("h-7 w-28 rounded-lg", isDark ? "bg-slate-700" : "bg-gray-200")} />
      </div>
    </div>
  );
}

/* ================================================================== */
/*  CopyPromptSection — collapsible section with copy button           */
/* ================================================================== */
function CopyPromptSection({ label, content, icon: Icon, isDark, copyLabel, copiedLabel }) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!content) return null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // clipboard API unavailable — silent fail
    }
  };

  return (
    <div
      className={cn(
        "rounded-lg border overflow-hidden",
        isDark ? "border-slate-700" : "border-gray-200"
      )}
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className={cn(
          "w-full flex items-center justify-between px-3 py-2.5 text-sm font-medium transition-colors",
          isDark
            ? "text-slate-300 hover:bg-slate-700/50"
            : "text-gray-700 hover:bg-gray-50"
        )}
      >
        <div className="flex items-center gap-2">
          <Icon size={13} className={isDark ? "text-purple-400" : "text-purple-500"} />
          <span>{label}</span>
        </div>
        {open ? (
          <ChevronUp size={13} className={isDark ? "text-slate-500" : "text-gray-400"} />
        ) : (
          <ChevronDown size={13} className={isDark ? "text-slate-500" : "text-gray-400"} />
        )}
      </button>

      {open && (
        <div
          className={cn(
            "px-3 pb-3 border-t",
            isDark ? "border-slate-700" : "border-gray-100"
          )}
        >
          <p
            className={cn(
              "text-xs leading-relaxed mt-2.5 mb-2.5 whitespace-pre-wrap break-words",
              isDark ? "text-slate-400" : "text-gray-600"
            )}
          >
            {content}
          </p>
          <button
            type="button"
            onClick={handleCopy}
            className={cn(
              "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition-colors",
              copied
                ? isDark
                  ? "bg-green-500/15 text-green-400"
                  : "bg-green-100 text-green-700"
                : isDark
                ? "bg-white/8 text-slate-300 hover:bg-white/12"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            )}
          >
            {copied ? <Check size={11} /> : <Copy size={11} />}
            {copied ? copiedLabel : copyLabel}
          </button>
        </div>
      )}
    </div>
  );
}

/* ================================================================== */
/*  IntelCard — single competitor_intel row                            */
/* ================================================================== */
function IntelCard({ item, isDark, lang, t, onGenerate, isGenerating }) {
  const cfg = SOURCE_CFG[item.source] || SOURCE_CFG.website;
  const sourceBadge = isDark ? cfg.dark : cfg.light;
  const SourceIcon = cfg.Icon;
  const sourceLabel = t[item.source] || item.source;

  return (
    <div
      className={cn(
        "rounded-xl border p-5 flex flex-col gap-3 transition-shadow hover:shadow-md",
        isDark
          ? "bg-slate-800 border-slate-700"
          : "bg-white border-gray-200 shadow-sm"
      )}
    >
      {/* Source badge + engagement */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <span
          className={cn(
            "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold",
            sourceBadge
          )}
        >
          <SourceIcon size={11} />
          {sourceLabel}
        </span>
        {item.engagement_score != null && (
          <span
            className={cn(
              "inline-flex items-center gap-1 text-xs",
              isDark ? "text-slate-400" : "text-gray-500"
            )}
          >
            <TrendingUp size={11} />
            {item.engagement_score}
          </span>
        )}
      </div>

      {/* Title */}
      <h3
        className={cn(
          "font-semibold text-sm leading-snug line-clamp-2",
          isDark ? "text-white" : "text-gray-900"
        )}
        dir={lang === "ar" ? "rtl" : "ltr"}
      >
        {item.original_title || item.topic || "\u2014"}
      </h3>

      {/* Topic pill */}
      {item.topic && (
        <span
          className={cn(
            "self-start inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium",
            isDark
              ? "bg-indigo-500/15 text-indigo-400"
              : "bg-indigo-100 text-indigo-600"
          )}
        >
          <Hash size={10} />
          {item.topic}
        </span>
      )}

      {/* Writing style notes */}
      {item.writing_style_notes && (
        <p
          className={cn(
            "text-xs leading-relaxed line-clamp-3",
            isDark ? "text-slate-400" : "text-gray-500"
          )}
          dir={lang === "ar" ? "rtl" : "ltr"}
        >
          {item.writing_style_notes}
        </p>
      )}

      {/* URL */}
      {item.original_url && (
        <a
          href={item.original_url}
          target="_blank"
          rel="noopener noreferrer"
          className={cn(
            "text-xs truncate",
            isDark
              ? "text-blue-400 hover:text-blue-300"
              : "text-blue-600 hover:text-blue-700"
          )}
          dir="ltr"
        >
          {item.original_url}
        </a>
      )}

      {/* Generate button */}
      <button
        type="button"
        onClick={() => onGenerate(item.id)}
        disabled={isGenerating}
        className={cn(
          "mt-auto self-start inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all",
          isGenerating
            ? "opacity-60 cursor-not-allowed bg-gradient-to-r from-purple-600/60 to-blue-600/60 text-white"
            : "bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 hover:shadow-md"
        )}
      >
        {isGenerating ? (
          <>
            <Loader2 size={12} className="animate-spin" />
            {t.generating}
          </>
        ) : (
          <>
            <Sparkles size={12} />
            {t.generateContent} →
          </>
        )}
      </button>
    </div>
  );
}

/* ================================================================== */
/*  SuggestionCard — single content_suggestions row                    */
/* ================================================================== */
function SuggestionCard({ item, isDark, lang, isRTL, t, onReject, onApprove, isRejecting, isApproving }) {
  const [showFullContent, setShowFullContent] = useState(false);
  const [showAllHooks, setShowAllHooks] = useState(false);

  /* Platform badge */
  const platCfg = PLATFORM_CFG[item.platform] || PLATFORM_CFG.blog;
  const platBadge = isDark ? platCfg.dark : platCfg.light;
  const PlatIcon = platCfg.Icon;
  const platLabel = t[item.platform] || item.platform;

  /* Status badge */
  const statCfg = STATUS_CFG[item.status] || STATUS_CFG.pending;
  const statBadge = isDark ? statCfg.dark : statCfg.light;
  const statusLabel = t[item.status] || item.status;

  /* Content preview */
  const contentAr = item.content_ar || "";
  const isLong = contentAr.length > 150;
  const preview = showFullContent ? contentAr : contentAr.slice(0, 150);

  /* Hooks — stored as jsonb (array) */
  let hooks = [];
  try {
    if (Array.isArray(item.hooks)) {
      hooks = item.hooks;
    } else if (typeof item.hooks === "string") {
      const parsed = JSON.parse(item.hooks);
      hooks = Array.isArray(parsed) ? parsed : [];
    }
  } catch {
    hooks = [];
  }
  const visibleHooks = showAllHooks ? hooks : hooks.slice(0, 3);
  const hiddenCount = hooks.length - 3;

  /* Relative date */
  let relDate = "";
  try {
    if (item.created_at) {
      relDate = formatDistanceToNow(new Date(item.created_at), { addSuffix: true });
    }
  } catch {
    relDate = "";
  }

  const isRejected = item.status === "rejected";
  const isPublished = item.status === "published";
  const hasCreativePrompts =
    item.banana_image_prompt ||
    item.carousel_prompt ||
    item.sora_video_prompt ||
    item.vue3_animation_prompt;

  return (
    <div
      className={cn(
        "rounded-xl border shadow-md flex flex-col overflow-hidden",
        isDark ? "bg-slate-800 border-slate-700" : "bg-white border-gray-200"
      )}
    >
      {/* ---- Card header ---- */}
      <div
        className={cn(
          "px-5 pt-4 pb-3 border-b",
          isDark ? "border-slate-700" : "border-gray-100"
        )}
      >
        {/* Badges row */}
        <div className="flex items-start justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2 flex-wrap">
            <span
              className={cn(
                "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold",
                platBadge
              )}
            >
              <PlatIcon size={11} />
              {platLabel}
            </span>
            <span
              className={cn(
                "inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium",
                statBadge
              )}
            >
              {statusLabel}
            </span>
          </div>
          {relDate && (
            <span
              className={cn(
                "text-xs shrink-0",
                isDark ? "text-slate-500" : "text-gray-400"
              )}
            >
              {relDate}
            </span>
          )}
        </div>

        {/* Titles */}
        <div className="mt-3 space-y-0.5">
          {item.title_ar && (
            <h3
              className={cn(
                "font-bold text-base leading-snug",
                isDark ? "text-white" : "text-gray-900"
              )}
              dir="rtl"
            >
              {item.title_ar}
            </h3>
          )}
          {item.title_en && (
            <p
              className={cn(
                "text-sm",
                isDark ? "text-slate-400" : "text-gray-500"
              )}
              dir="ltr"
            >
              {item.title_en}
            </p>
          )}
        </div>
      </div>

      {/* ---- Card body ---- */}
      <div className="px-5 py-4 flex-1 flex flex-col gap-4">
        {/* Content preview */}
        {contentAr && (
          <div>
            <p
              className={cn(
                "text-sm leading-relaxed",
                isDark ? "text-slate-300" : "text-gray-700"
              )}
              dir="rtl"
            >
              {preview}
              {isLong && !showFullContent && (
                <span className={isDark ? "text-slate-500" : "text-gray-400"}>
                  ...
                </span>
              )}
            </p>
            {isLong && (
              <button
                type="button"
                onClick={() => setShowFullContent((v) => !v)}
                className={cn(
                  "text-xs mt-1 font-medium",
                  isDark
                    ? "text-blue-400 hover:text-blue-300"
                    : "text-blue-600 hover:text-blue-700"
                )}
              >
                {showFullContent ? t.showLess : t.showMore}
              </button>
            )}
          </div>
        )}

        {/* Hooks */}
        {hooks.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2.5">
              <div
                className={cn(
                  "flex-1 h-px",
                  isDark ? "bg-slate-700" : "bg-gray-200"
                )}
              />
              <span
                className={cn(
                  "text-xs font-semibold uppercase tracking-wider px-2",
                  isDark ? "text-slate-500" : "text-gray-400"
                )}
              >
                {t.hooks}
              </span>
              <div
                className={cn(
                  "flex-1 h-px",
                  isDark ? "bg-slate-700" : "bg-gray-200"
                )}
              />
            </div>
            <ol className="space-y-1.5">
              {visibleHooks.map((hook, i) => (
                <li
                  key={i}
                  className={cn(
                    "text-xs leading-relaxed flex gap-2",
                    isDark ? "text-slate-300" : "text-gray-600"
                  )}
                  dir="rtl"
                >
                  <span
                    className={cn(
                      "font-bold shrink-0",
                      isDark ? "text-purple-400" : "text-purple-500"
                    )}
                  >
                    {i + 1}.
                  </span>
                  <span>{hook}</span>
                </li>
              ))}
            </ol>
            {hiddenCount > 0 && !showAllHooks && (
              <button
                type="button"
                onClick={() => setShowAllHooks(true)}
                className={cn(
                  "text-xs mt-2 font-medium",
                  isDark
                    ? "text-slate-400 hover:text-slate-300"
                    : "text-gray-500 hover:text-gray-600"
                )}
              >
                +{hiddenCount} {lang === "ar" ? "أكثر" : "more"}
              </button>
            )}
          </div>
        )}

        {/* Creative prompts */}
        {hasCreativePrompts && (
          <div>
            <div className="flex items-center gap-2 mb-2.5">
              <div
                className={cn(
                  "flex-1 h-px",
                  isDark ? "bg-slate-700" : "bg-gray-200"
                )}
              />
              <span
                className={cn(
                  "text-xs font-semibold uppercase tracking-wider px-2",
                  isDark ? "text-slate-500" : "text-gray-400"
                )}
              >
                {t.creativePrompts}
              </span>
              <div
                className={cn(
                  "flex-1 h-px",
                  isDark ? "bg-slate-700" : "bg-gray-200"
                )}
              />
            </div>
            <div className="space-y-1.5">
              <CopyPromptSection
                label={t.imagePrompt}
                content={item.banana_image_prompt}
                icon={Image}
                isDark={isDark}
                copyLabel={t.copy}
                copiedLabel={t.copied}
              />
              <CopyPromptSection
                label={t.carouselPrompt}
                content={item.carousel_prompt}
                icon={LayoutGrid}
                isDark={isDark}
                copyLabel={t.copy}
                copiedLabel={t.copied}
              />
              <CopyPromptSection
                label={t.videoPrompt}
                content={item.sora_video_prompt}
                icon={Video}
                isDark={isDark}
                copyLabel={t.copy}
                copiedLabel={t.copied}
              />
              <CopyPromptSection
                label={t.animationPrompt}
                content={item.vue3_animation_prompt}
                icon={Zap}
                isDark={isDark}
                copyLabel={t.copy}
                copiedLabel={t.copied}
              />
            </div>
          </div>
        )}
      </div>

      {/* ---- Card footer — action buttons ---- */}
      {!isRejected && (
        <div
          className={cn(
            "px-5 py-3 border-t flex items-center gap-2 flex-wrap",
            isDark
              ? "border-slate-700 bg-slate-800/50"
              : "border-gray-100 bg-gray-50/60"
          )}
        >
          {/* Reject */}
          {!isPublished && (
            <button
              type="button"
              onClick={() => onReject(item.id)}
              disabled={isRejecting}
              className={cn(
                "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors",
                isRejecting
                  ? "opacity-50 cursor-not-allowed bg-red-500/10 text-red-400"
                  : "bg-red-500/12 text-red-400 hover:bg-red-500/22"
              )}
            >
              {isRejecting ? (
                <Loader2 size={12} className="animate-spin" />
              ) : (
                <XCircle size={12} />
              )}
              {t.reject}
            </button>
          )}

          {/* Edit in Blog */}
          {item.blog_post_id && (
            <Link
              to={`/admin/blog/edit/${item.blog_post_id}`}
              className={cn(
                "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors",
                isDark
                  ? "bg-white/8 text-slate-300 hover:bg-white/12"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              )}
            >
              <PencilLine size={12} />
              {t.editInBlog}
            </Link>
          )}

          {/* Approve → Blog Draft */}
          {!isPublished && (
            <button
              type="button"
              onClick={() => onApprove(item.id)}
              disabled={isApproving}
              className={cn(
                "ml-auto inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all",
                isApproving
                  ? "opacity-60 cursor-not-allowed bg-green-600/50 text-white"
                  : "bg-gradient-to-r from-green-600 to-emerald-600 text-white hover:from-green-700 hover:to-emerald-700 hover:shadow-md"
              )}
            >
              {isApproving ? (
                <Loader2 size={12} className="animate-spin" />
              ) : (
                <CheckCircle2 size={12} />
              )}
              {t.approveBlogDraft}
            </button>
          )}

          {/* Published — just show edit */}
          {isPublished && item.blog_post_id && (
            <Link
              to={`/admin/blog/edit/${item.blog_post_id}`}
              className={cn(
                "ml-auto inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors",
                "bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25"
              )}
            >
              <PencilLine size={12} />
              {t.editInBlog}
            </Link>
          )}
        </div>
      )}

      {/* Rejected state footer */}
      {isRejected && (
        <div
          className={cn(
            "px-5 py-2.5 border-t flex items-center gap-2",
            isDark ? "border-slate-700" : "border-gray-100"
          )}
        >
          <XCircle size={13} className="text-red-400" />
          <span
            className={cn(
              "text-xs",
              isDark ? "text-slate-500" : "text-gray-400"
            )}
          >
            {t.rejected}
          </span>
        </div>
      )}
    </div>
  );
}

/* ================================================================== */
/*  SectionDivider — horizontal rule with label                       */
/* ================================================================== */
function SectionDivider({ label, isDark }) {
  return (
    <div className="flex items-center gap-3 my-1">
      <div className={cn("flex-1 h-px", isDark ? "bg-slate-700" : "bg-gray-200")} />
      <span
        className={cn(
          "text-xs uppercase tracking-widest font-semibold",
          isDark ? "text-slate-600" : "text-gray-400"
        )}
      >
        {label}
      </span>
      <div className={cn("flex-1 h-px", isDark ? "bg-slate-700" : "bg-gray-200")} />
    </div>
  );
}

/* ================================================================== */
/*  CompetitorDashboard — main page component                          */
/* ================================================================== */
export default function CompetitorDashboard() {
  const { lang = "ar", theme = "dark" } = useOutletContext() || {};
  const t = L[lang] || L.ar;
  const isDark = theme === "dark";
  const isRTL = lang === "ar";
  const navigate = useNavigate();
  const qc = useQueryClient();

  /* ---- UI state ---- */
  const [activeTab, setActiveTab] = useState("intel");
  const [platformFilter, setPlatformFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [isScraping, setIsScraping] = useState(false);
  const [generatingIds, setGeneratingIds] = useState(new Set());
  const [rejectingId, setRejectingId] = useState(null);
  const [approvingId, setApprovingId] = useState(null);

  /* ---- Data queries ---- */
  const {
    data: intel = [],
    isLoading: intelLoading,
  } = useQuery({
    queryKey: ["competitor-intel"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("competitor_intel")
        .select("*")
        .order("scraped_at", { ascending: false })
        .limit(50);
      if (error) throw error;
      return data || [];
    },
  });

  const {
    data: suggestions = [],
    isLoading: suggestionsLoading,
  } = useQuery({
    queryKey: ["content-suggestions"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("content_suggestions")
        .select("*")
        .order("created_at", { ascending: false });
      if (error) throw error;
      return data || [];
    },
  });

  /* ---- Reject mutation ---- */
  const rejectMutation = useMutation({
    mutationFn: async (id) => {
      const { error } = await supabase
        .from("content_suggestions")
        .update({ status: "rejected" })
        .eq("id", id);
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["content-suggestions"] });
      toast.success(lang === "ar" ? "تم رفض الاقتراح" : "Suggestion rejected");
    },
    onError: () => {
      toast.error(lang === "ar" ? "فشل رفض الاقتراح" : "Failed to reject suggestion");
    },
    onSettled: () => setRejectingId(null),
  });

  /* ---- Derived stats ---- */
  const pendingCount = useMemo(
    () => suggestions.filter((s) => s.status === "pending").length,
    [suggestions]
  );
  const approvedPublishedCount = useMemo(
    () => suggestions.filter((s) => s.status === "approved" || s.status === "published").length,
    [suggestions]
  );
  const lastScrapedDate = useMemo(() => {
    if (!intel.length) return null;
    const first = intel[0];
    if (!first?.scraped_at) return null;
    try {
      return formatDistanceToNow(new Date(first.scraped_at), { addSuffix: true });
    } catch {
      return null;
    }
  }, [intel]);

  /* ---- Filtered suggestions ---- */
  const filteredSuggestions = useMemo(() => {
    return suggestions.filter((s) => {
      if (platformFilter !== "all" && s.platform !== platformFilter) return false;
      if (statusFilter !== "all" && s.status !== statusFilter) return false;
      return true;
    });
  }, [suggestions, platformFilter, statusFilter]);

  /* ---- Handlers ---- */
  const handleScrapeNow = async () => {
    const webhookUrl = import.meta.env.VITE_N8N_COMPETITOR_SCRAPER_WEBHOOK;
    if (!webhookUrl) {
      toast.error(
        lang === "ar"
          ? "رابط webhook الرصد غير مضبوط"
          : "Scraper webhook URL not configured"
      );
      return;
    }
    setIsScraping(true);
    try {
      await fetch(webhookUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      toast.success(
        lang === "ar"
          ? "تم تشغيل الرصد بنجاح!"
          : "Scraper triggered successfully!"
      );
      qc.invalidateQueries({ queryKey: ["competitor-intel"] });
    } catch {
      toast.error(
        lang === "ar" ? "فشل تشغيل الرصد" : "Failed to trigger scraper"
      );
    }
    setIsScraping(false);
  };

  const handleGenerate = async (intelId) => {
    const webhookUrl = import.meta.env.VITE_N8N_COMPETITOR_GENERATE_WEBHOOK;
    if (!webhookUrl) {
      toast.error(
        lang === "ar"
          ? "رابط webhook التوليد غير مضبوط"
          : "Generate webhook not configured"
      );
      return;
    }
    setGeneratingIds((prev) => new Set([...prev, intelId]));
    try {
      await fetch(webhookUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ intel_id: intelId, platform: "all" }),
      });
      qc.invalidateQueries({ queryKey: ["content-suggestions"] });
      toast.success(
        lang === "ar"
          ? "تم توليد المحتوى بنجاح!"
          : "Content generated successfully!"
      );
    } catch {
      toast.error(
        lang === "ar" ? "فشل توليد المحتوى" : "Failed to generate content"
      );
    }
    setGeneratingIds((prev) => {
      const next = new Set(prev);
      next.delete(intelId);
      return next;
    });
  };

  const handleApprove = async (suggestionId) => {
    const webhookUrl = import.meta.env.VITE_N8N_BLOG_PUBLISHER_WEBHOOK;
    if (!webhookUrl) {
      toast.error(
        lang === "ar"
          ? "رابط webhook نشر المدونة غير مضبوط"
          : "Blog publisher webhook not configured"
      );
      return;
    }
    setApprovingId(suggestionId);
    try {
      const res = await fetch(webhookUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ suggestion_id: suggestionId }),
      });
      const responseData = await res.json().catch(() => ({}));

      /* Update status in Supabase */
      const { error } = await supabase
        .from("content_suggestions")
        .update({ status: "approved", approved_at: new Date().toISOString() })
        .eq("id", suggestionId);
      if (error) throw error;

      qc.invalidateQueries({ queryKey: ["content-suggestions"] });
      toast.success(
        lang === "ar"
          ? "تم الاعتماد وإنشاء مسودة المدونة!"
          : "Approved and blog draft created!"
      );

      /* Navigate to blog edit page if blog_post_id returned */
      const blogPostId =
        responseData?.blog_post_id ||
        responseData?.id ||
        responseData?.data?.blog_post_id;
      if (blogPostId) {
        navigate(`/admin/blog/edit/${blogPostId}`);
      }
    } catch {
      toast.error(
        lang === "ar" ? "فشل عملية الاعتماد" : "Failed to approve suggestion"
      );
    }
    setApprovingId(null);
  };

  const handleReject = (id) => {
    setRejectingId(id);
    rejectMutation.mutate(id);
  };

  /* ---- Tab options ---- */
  const tabs = [
    { key: "intel", label: t.thmanyahContent },
    { key: "suggestions", label: t.contentSuggestions },
  ];

  const platformOptions = ["all", "blog", "tiktok", "instagram", "facebook", "linkedin"];
  const statusOptions = ["all", "pending", "approved", "rejected", "published"];

  /* ================================================================ */
  /*  Render                                                           */
  /* ================================================================ */
  return (
    <div className="max-w-7xl mx-auto" dir={isRTL ? "rtl" : "ltr"}>

      {/* ---- Page header ---- */}
      <div className="flex flex-wrap items-start justify-between gap-4 mb-8">
        <div>
          <h1
            className={cn(
              "text-3xl font-black",
              isDark ? "text-white" : "text-gray-900"
            )}
          >
            {t.competitorDashboard}
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

        {/* Scrape Now button */}
        <button
          type="button"
          onClick={handleScrapeNow}
          disabled={isScraping}
          className={cn(
            "inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all",
            isScraping
              ? "opacity-60 cursor-not-allowed bg-gradient-to-r from-orange-600/60 to-red-600/60 text-white"
              : "bg-gradient-to-r from-orange-500 to-red-500 text-white hover:from-orange-600 hover:to-red-600 hover:shadow-lg"
          )}
        >
          {isScraping ? (
            <Loader2 size={15} className="animate-spin" />
          ) : (
            <RefreshCw size={15} />
          )}
          {isScraping ? t.scraping : t.scrapeNow}
        </button>
      </div>

      {/* ---- Stat cards ---- */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          title={t.totalIntel}
          value={intel.length}
          icon={Database}
          color="blue"
          loading={intelLoading}
          theme={theme}
          lang={lang}
        />
        <StatCard
          title={t.pendingSuggestions}
          value={pendingCount}
          icon={Clock}
          color="amber"
          loading={suggestionsLoading}
          theme={theme}
          lang={lang}
        />
        <StatCard
          title={t.approvedPublished}
          value={approvedPublishedCount}
          icon={CheckCircle2}
          color="green"
          loading={suggestionsLoading}
          theme={theme}
          lang={lang}
        />
        <StatCard
          title={t.lastScraped}
          value={
            intelLoading
              ? null
              : lastScrapedDate || t.neverScraped
          }
          icon={RefreshCw}
          color="purple"
          loading={intelLoading}
          theme={theme}
          lang={lang}
        />
      </div>

      {/* ---- Tabs ---- */}
      <div
        className={cn(
          "flex gap-1 p-1 rounded-xl mb-6 w-fit",
          isDark ? "bg-slate-800/80" : "bg-gray-100"
        )}
      >
        {tabs.map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => setActiveTab(tab.key)}
            className={cn(
              "px-5 py-2 rounded-lg text-sm font-semibold transition-all",
              activeTab === tab.key
                ? isDark
                  ? "bg-slate-700 text-white shadow-sm"
                  : "bg-white text-gray-900 shadow-sm"
                : isDark
                ? "text-slate-400 hover:text-slate-200"
                : "text-gray-500 hover:text-gray-700"
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ================================================================ */}
      {/* TAB 1: Thmanyah Content (competitor_intel)                       */}
      {/* ================================================================ */}
      {activeTab === "intel" && (
        <>
          {intelLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <SkeletonCard key={i} isDark={isDark} />
              ))}
            </div>
          ) : intel.length === 0 ? (
            /* Empty state */
            <div
              className={cn(
                "rounded-xl border p-16 flex flex-col items-center justify-center gap-5 text-center",
                isDark
                  ? "bg-slate-800/40 border-slate-700"
                  : "bg-gray-50 border-gray-200"
              )}
            >
              <div
                className={cn(
                  "w-20 h-20 rounded-2xl flex items-center justify-center",
                  isDark ? "bg-slate-700" : "bg-gray-200"
                )}
              >
                <Database
                  size={32}
                  className={isDark ? "text-slate-500" : "text-gray-400"}
                />
              </div>
              <div>
                <h3
                  className={cn(
                    "font-bold text-lg",
                    isDark ? "text-white" : "text-gray-900"
                  )}
                >
                  {t.noIntelYet}
                </h3>
              </div>
              <button
                type="button"
                onClick={handleScrapeNow}
                disabled={isScraping}
                className={cn(
                  "inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all",
                  isScraping
                    ? "opacity-60 cursor-not-allowed bg-orange-500/50 text-white"
                    : "bg-gradient-to-r from-orange-500 to-red-500 text-white hover:from-orange-600 hover:to-red-600"
                )}
              >
                {isScraping ? (
                  <Loader2 size={15} className="animate-spin" />
                ) : (
                  <RefreshCw size={15} />
                )}
                {isScraping ? t.scraping : t.scrapeNow}
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {intel.map((item) => (
                <IntelCard
                  key={item.id}
                  item={item}
                  isDark={isDark}
                  lang={lang}
                  t={t}
                  onGenerate={handleGenerate}
                  isGenerating={generatingIds.has(item.id)}
                />
              ))}
            </div>
          )}
        </>
      )}

      {/* ================================================================ */}
      {/* TAB 2: Content Suggestions                                       */}
      {/* ================================================================ */}
      {activeTab === "suggestions" && (
        <>
          {/* Filter bar */}
          <div className="flex flex-wrap items-center gap-4 mb-6">
            {/* Platform filter */}
            <div className="flex flex-wrap gap-1.5">
              <span
                className={cn(
                  "text-xs font-medium self-center mr-1",
                  isDark ? "text-slate-500" : "text-gray-400"
                )}
              >
                {t.platform}:
              </span>
              {platformOptions.map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => setPlatformFilter(p)}
                  className={cn(
                    "px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors",
                    platformFilter === p
                      ? "bg-purple-600 text-white"
                      : isDark
                      ? "bg-white/8 text-slate-300 hover:bg-white/12"
                      : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  )}
                >
                  {t[p] || p}
                </button>
              ))}
            </div>

            <div
              className={cn(
                "w-px h-5",
                isDark ? "bg-slate-700" : "bg-gray-200"
              )}
            />

            {/* Status filter */}
            <div className="flex flex-wrap gap-1.5">
              <span
                className={cn(
                  "text-xs font-medium self-center mr-1",
                  isDark ? "text-slate-500" : "text-gray-400"
                )}
              >
                {t.status}:
              </span>
              {statusOptions.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setStatusFilter(s)}
                  className={cn(
                    "px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors",
                    statusFilter === s
                      ? "bg-blue-600 text-white"
                      : isDark
                      ? "bg-white/8 text-slate-300 hover:bg-white/12"
                      : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  )}
                >
                  {t[s] || s}
                </button>
              ))}
            </div>
          </div>

          {/* Grid */}
          {suggestionsLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <SkeletonCard key={i} isDark={isDark} />
              ))}
            </div>
          ) : suggestions.length === 0 ? (
            /* Empty state — no suggestions at all */
            <div
              className={cn(
                "rounded-xl border p-16 flex flex-col items-center justify-center gap-5 text-center",
                isDark
                  ? "bg-slate-800/40 border-slate-700"
                  : "bg-gray-50 border-gray-200"
              )}
            >
              <div
                className={cn(
                  "w-20 h-20 rounded-2xl flex items-center justify-center",
                  isDark ? "bg-slate-700" : "bg-gray-200"
                )}
              >
                <Sparkles
                  size={32}
                  className={isDark ? "text-slate-500" : "text-gray-400"}
                />
              </div>
              <div>
                <h3
                  className={cn(
                    "font-bold text-lg",
                    isDark ? "text-white" : "text-gray-900"
                  )}
                >
                  {t.noSuggestionsYet}
                </h3>
                <p
                  className={cn(
                    "text-sm mt-1",
                    isDark ? "text-slate-500" : "text-gray-400"
                  )}
                >
                  {lang === "ar"
                    ? "انتقل إلى تبويب «محتوى ثمانية» واضغط «توليد محتوى»"
                    : 'Go to the "Thmanyah Content" tab and click "Generate Content"'}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setActiveTab("intel")}
                className={cn(
                  "inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-colors",
                  isDark
                    ? "bg-white/10 text-white hover:bg-white/15"
                    : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                )}
              >
                {t.thmanyahContent}
              </button>
            </div>
          ) : filteredSuggestions.length === 0 ? (
            /* Empty state — filters returned nothing */
            <div
              className={cn(
                "rounded-xl border p-12 flex flex-col items-center justify-center gap-3 text-center",
                isDark
                  ? "bg-slate-800/40 border-slate-700"
                  : "bg-gray-50 border-gray-200"
              )}
            >
              <p
                className={cn(
                  "font-medium",
                  isDark ? "text-slate-400" : "text-gray-500"
                )}
              >
                {t.noResults}
              </p>
              <button
                type="button"
                onClick={() => {
                  setPlatformFilter("all");
                  setStatusFilter("all");
                }}
                className={cn(
                  "text-sm font-semibold",
                  isDark
                    ? "text-purple-400 hover:text-purple-300"
                    : "text-purple-600 hover:text-purple-700"
                )}
              >
                {lang === "ar" ? "مسح الفلاتر" : "Clear filters"}
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {filteredSuggestions.map((item) => (
                <SuggestionCard
                  key={item.id}
                  item={item}
                  isDark={isDark}
                  lang={lang}
                  isRTL={isRTL}
                  t={t}
                  onReject={handleReject}
                  onApprove={handleApprove}
                  isRejecting={rejectingId === item.id}
                  isApproving={approvingId === item.id}
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
