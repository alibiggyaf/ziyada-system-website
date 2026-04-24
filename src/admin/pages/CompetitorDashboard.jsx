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
  CalendarDays,
  MessageSquare,
} from "lucide-react";

/* ================================================================== */
/*  Bilingual labels                                                   */
/* ================================================================== */
const L = {
  ar: {
    competitorDashboard: "تحليل المنافسين",
    subtitle: "فهم محتوى ثمانية وتحويله إلى أفكار واضحة وجاهزة للنشر",
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
    hooks: "افتتاحيات قوية",
    imagePrompt: "وصف تصميم الصورة",
    carouselPrompt: "وصف تصميم الكاروسيل",
    videoPrompt: "وصف فكرة الفيديو",
    animationPrompt: "وصف الحركة التفاعلية",
    copy: "نسخ",
    copied: "تم النسخ!",
    noIntelYet: "لا توجد بيانات حتى الآن. اضغط «رصد الآن» لبدء جمع محتوى ثمانية.",
    noSuggestionsYet: "لا توجد اقتراحات بعد. ابدأ من تبويب محتوى ثمانية ثم اضغط «توليد محتوى».",
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
    creativePrompts: "أوامر إبداعية جاهزة",
    scraping: "جارٍ الرصد...",
    generating: "جارٍ التوليد...",
    approving: "جارٍ الاعتماد...",
    platform: "المنصة",
    status: "الحالة",
    noResults: "لا توجد نتائج مطابقة",
    scrapeNowHint: "يجمع آخر محتوى من ثمانية ويحدّث البيانات في الصفحة.",
    generateHint: "ينتج عناوين ومحتوى واقتراحات قابلة للنشر اعتمادًا على هذا العنصر.",
    approveHint: "يعتمد الاقتراح وينشئ مسودة جاهزة في المدونة.",
    rejectHint: "يرفض الاقتراح الحالي ويخفيه من مسار النشر.",
    tabIntelHint: "يعرض المحتوى المرصود من ثمانية مع خيار التوليد.",
    tabSuggestionsHint: "يعرض الاقتراحات الجاهزة مع خيارات الاعتماد والرفض.",
    filterPlatformHint: "فلترة النتائج حسب المنصة.",
    filterStatusHint: "فلترة النتائج حسب حالة الاقتراح.",
    plannerTitle: "وكيل التقويم الشهري للمحتوى",
    plannerSubtitle:
      "أدخل المنافسين (روابط أو أسماء)، وحدد عدد القطع لكل منصة، ثم شغّل خطة شهر كامل جاهزة للنسخ.",
    competitorInputLabel: "المنافسون",
    competitorInputPlaceholder:
      "مثال: thmanyah.com, competitor.com, https://instagram.com/brand",
    monthLabel: "الشهر المستهدف",
    runPlanner: "توليد تقويم شهر كامل",
    plannerRunning: "جارٍ توليد التقويم...",
    qtyPerPlatform: "عدد القطع لكل منصة",
    calendarTab: "تقويم الشهر",
    plannerHint:
      "يشغّل الوكيل الذكي لتحليل المنافسين وإنتاج خطة شهرية مع نصوص ومنشورات جاهزة.",
    calendarEmpty:
      "لا توجد عناصر تقويم لهذا الشهر بعد. شغّل وكيل التخطيط أولاً.",
    agentReply: "آخر رد من الوكيل",
    copyAll: "نسخ الحزمة كاملة",
    postType: "نوع المنشور",
    keywords: "الكلمات المفتاحية",
    hashtags: "الهاشتاغات",
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
    creativePrompts: "Creative Briefs",
    scraping: "Scraping...",
    generating: "Generating...",
    approving: "Approving...",
    platform: "Platform",
    status: "Status",
    noResults: "No matching results",
    scrapeNowHint: "Fetch the latest Thmanyah content and refresh this dashboard.",
    generateHint: "Generate publishable ideas, titles, and drafts from this intel item.",
    approveHint: "Approve this suggestion and create a blog draft.",
    rejectHint: "Reject this suggestion and remove it from publishing flow.",
    tabIntelHint: "View scraped Thmanyah items and generate ideas from them.",
    tabSuggestionsHint: "View generated suggestions and manage approval status.",
    filterPlatformHint: "Filter results by platform.",
    filterStatusHint: "Filter results by current suggestion status.",
    plannerTitle: "Monthly Content Calendar Agent",
    plannerSubtitle:
      "Enter competitors (links or names), set quantity per platform, then generate a full month of ready-to-copy content.",
    competitorInputLabel: "Competitors",
    competitorInputPlaceholder:
      "Example: thmanyah.com, competitor.com, https://instagram.com/brand",
    monthLabel: "Target Month",
    runPlanner: "Generate Monthly Calendar",
    plannerRunning: "Generating calendar...",
    qtyPerPlatform: "Quantity per Platform",
    calendarTab: "Monthly Calendar",
    plannerHint:
      "Runs the agent workflow to analyze competitors and produce a one-month content package.",
    calendarEmpty:
      "No calendar items for this month yet. Run the planner agent first.",
    agentReply: "Latest Agent Reply",
    copyAll: "Copy Full Package",
    postType: "Post Type",
    keywords: "Keywords",
    hashtags: "Hashtags",
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
        title={t.generateHint}
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
              title={t.rejectHint}
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
              title={t.approveHint}
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
  const [competitorInput, setCompetitorInput] = useState("");
  const [targetMonth, setTargetMonth] = useState(new Date().toISOString().slice(0, 7));
  const [monthlyCounts, setMonthlyCounts] = useState({
    instagram: 10,
    x: 8,
    tiktok: 8,
    facebook: 6,
    linkedin: 6,
  });
  const [isPlannerRunning, setIsPlannerRunning] = useState(false);
  const [latestAgentReply, setLatestAgentReply] = useState("");

  const resolveWebhookUrl = (path) => {
    if (!path) return "";
    if (path.startsWith("http")) return path;
    const base = import.meta.env.VITE_N8N_HOST || "";
    return `${base}${path}`;
  };

  const postWebhook = async (path, body) => {
    const url = resolveWebhookUrl(path);
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 20000);
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body || {}),
        signal: controller.signal,
      });
      if (!res.ok) throw new Error(`Webhook failed: ${res.status}`);
      return res;
    } finally {
      clearTimeout(timer);
    }
  };
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

  const {
    data: calendarEntries = [],
    isLoading: calendarLoading,
  } = useQuery({
    queryKey: ["content-calendar-entries", targetMonth],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("content_calendar_entries")
        .select("*")
        .eq("target_month", targetMonth)
        .order("publish_date", { ascending: true });
      if (error) {
        if (error.code === "42P01") return [];
        throw error;
      }
      return data || [];
    },
  });

  const {
    data: agentConversations = [],
  } = useQuery({
    queryKey: ["agent-conversations"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("agent_conversations")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(8);
      if (error) {
        if (error.code === "42P01") return [];
        throw error;
      }
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
      await postWebhook(webhookUrl, {});
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
    } finally {
      setIsScraping(false);
    }
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
      await postWebhook(webhookUrl, { intel_id: intelId, platform: "all" });
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
    } finally {
      setGeneratingIds((prev) => {
        const next = new Set(prev);
        next.delete(intelId);
        return next;
      });
    }
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

  const normalizeCompetitorInputs = (raw) =>
    raw
      .split(/[\n,]+/)
      .map((v) => v.trim())
      .filter(Boolean);

  const handleRunPlanner = async () => {
    const inputs = normalizeCompetitorInputs(competitorInput);
    if (!inputs.length) {
      toast.error(
        lang === "ar"
          ? "أدخل منافسًا واحدًا على الأقل (اسم أو رابط)"
          : "Please enter at least one competitor name or URL"
      );
      return;
    }

    const webhookPath =
      import.meta.env.VITE_N8N_COMPETITOR_AGENT_WEBHOOK ||
      import.meta.env.VITE_N8N_CONTENT_STRATEGY_WEBHOOK;
    if (!webhookPath) {
      toast.error(
        lang === "ar"
          ? "Webhook الوكيل غير مضبوط"
          : "Planner agent webhook is not configured"
      );
      return;
    }

    setIsPlannerRunning(true);
    try {
      const res = await postWebhook(webhookPath, {
        action: "generate_monthly_calendar",
        target_month: targetMonth,
        competitor_inputs: inputs,
        requested_counts: monthlyCounts,
        requested_platforms: ["instagram", "x", "tiktok", "facebook", "linkedin"],
        include_assets: true,
        include_newsletter: true,
        include_blog_article: true,
      });

      const responseData = await res.json().catch(() => ({}));
      const replyText =
        responseData?.message ||
        responseData?.summary ||
        (lang === "ar"
          ? "تم تشغيل الوكيل بنجاح. جارٍ تحديث نتائج التقويم."
          : "Agent was triggered successfully. Calendar results are updating.");
      setLatestAgentReply(replyText);

      const payloadSnapshot = {
        target_month: targetMonth,
        competitor_inputs: inputs,
        requested_counts: monthlyCounts,
      };

      const { error: insertError } = await supabase
        .from("agent_conversations")
        .insert({
          agent_type: "competitor_calendar",
          user_message: JSON.stringify(payloadSnapshot),
          agent_response: replyText,
          metadata: responseData,
        });
      if (insertError && insertError.code !== "42P01") {
        throw insertError;
      }

      qc.invalidateQueries({ queryKey: ["agent-conversations"] });
      qc.invalidateQueries({ queryKey: ["content-calendar-entries"] });
      toast.success(
        lang === "ar"
          ? "تم تشغيل وكيل التقويم الشهري"
          : "Monthly calendar agent triggered"
      );
    } catch (error) {
      toast.error(
        lang === "ar"
          ? "فشل تشغيل وكيل التقويم"
          : "Failed to run monthly planner agent"
      );
      console.error(error);
    } finally {
      setIsPlannerRunning(false);
    }
  };

  /* ---- Tab options ---- */
  const tabs = [
    { key: "intel", label: t.thmanyahContent },
    { key: "suggestions", label: t.contentSuggestions },
    { key: "calendar", label: t.calendarTab },
  ];

  const platformOptions = ["all", "blog", "tiktok", "instagram", "facebook", "linkedin"];
  const statusOptions = ["all", "pending", "approved", "rejected", "published"];

  /* ================================================================ */
  /*  Render                                                           */
  /* ================================================================ */
  return (
    <div className="max-w-7xl mx-auto" dir={isRTL ? "rtl" : "ltr"}>

      {/* ---- Monthly Planner Agent ---- */}
      <div
        className={cn(
          "rounded-xl border p-5 mb-6",
          isDark ? "bg-slate-800 border-slate-700" : "bg-white border-gray-200"
        )}
      >
        <div className="flex items-start gap-3 mb-4">
          <div
            className={cn(
              "w-10 h-10 rounded-lg flex items-center justify-center",
              isDark ? "bg-purple-500/15" : "bg-purple-100"
            )}
          >
            <MessageSquare size={18} className={isDark ? "text-purple-300" : "text-purple-700"} />
          </div>
          <div>
            <h2 className={cn("font-bold text-base", isDark ? "text-white" : "text-gray-900")}>{t.plannerTitle}</h2>
            <p className={cn("text-sm mt-1", isDark ? "text-slate-400" : "text-gray-500")}>{t.plannerSubtitle}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 space-y-2">
            <label className={cn("text-xs font-semibold", isDark ? "text-slate-300" : "text-gray-700")}>{t.competitorInputLabel}</label>
            <textarea
              value={competitorInput}
              onChange={(e) => setCompetitorInput(e.target.value)}
              placeholder={t.competitorInputPlaceholder}
              className={cn(
                "w-full min-h-28 rounded-lg px-3 py-2 text-sm border",
                isDark
                  ? "bg-slate-900 border-slate-700 text-slate-100 placeholder:text-slate-500"
                  : "bg-white border-gray-300 text-gray-900 placeholder:text-gray-400"
              )}
            />
            <p className={cn("text-xs", isDark ? "text-slate-500" : "text-gray-500")}>{t.plannerHint}</p>
          </div>

          <div className="space-y-3">
            <div>
              <label className={cn("text-xs font-semibold", isDark ? "text-slate-300" : "text-gray-700")}>{t.monthLabel}</label>
              <input
                type="month"
                value={targetMonth}
                onChange={(e) => setTargetMonth(e.target.value)}
                className={cn(
                  "mt-1 w-full rounded-lg px-3 py-2 text-sm border",
                  isDark ? "bg-slate-900 border-slate-700 text-slate-100" : "bg-white border-gray-300 text-gray-900"
                )}
              />
            </div>

            <div>
              <p className={cn("text-xs font-semibold mb-1.5", isDark ? "text-slate-300" : "text-gray-700")}>{t.qtyPerPlatform}</p>
              <div className="grid grid-cols-2 gap-2">
                {Object.keys(monthlyCounts).map((key) => (
                  <input
                    key={key}
                    type="number"
                    min="0"
                    value={monthlyCounts[key]}
                    onChange={(e) =>
                      setMonthlyCounts((prev) => ({
                        ...prev,
                        [key]: Number(e.target.value || 0),
                      }))
                    }
                    className={cn(
                      "rounded-lg px-2.5 py-2 text-xs border",
                      isDark ? "bg-slate-900 border-slate-700 text-slate-100" : "bg-white border-gray-300 text-gray-900"
                    )}
                    title={key}
                    placeholder={key}
                  />
                ))}
              </div>
            </div>

            <button
              type="button"
              onClick={handleRunPlanner}
              disabled={isPlannerRunning}
              className={cn(
                "w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all",
                isPlannerRunning
                  ? "opacity-60 cursor-not-allowed bg-gradient-to-r from-purple-600/60 to-blue-600/60 text-white"
                  : "bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700"
              )}
            >
              {isPlannerRunning ? <Loader2 size={14} className="animate-spin" /> : <CalendarDays size={14} />}
              {isPlannerRunning ? t.plannerRunning : t.runPlanner}
            </button>
          </div>
        </div>

        {(latestAgentReply || agentConversations.length > 0) && (
          <div
            className={cn(
              "mt-4 rounded-lg border px-3 py-2.5 text-sm",
              isDark ? "border-slate-700 bg-slate-900/50 text-slate-300" : "border-gray-200 bg-gray-50 text-gray-700"
            )}
          >
            <p className={cn("text-xs font-semibold mb-1", isDark ? "text-slate-400" : "text-gray-500")}>{t.agentReply}</p>
            <p>{latestAgentReply || agentConversations[0]?.agent_response}</p>
          </div>
        )}
      </div>

      {/* ---- Page header ---- */}
      <div className="flex flex-wrap items-start justify-between gap-4 mb-8">
        <div>
          <h1
            className={cn(
              "text-3xl font-black",
              isDark ? "text-white" : "text-gray-900"
            )}
            title={t.subtitle}
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
          title={t.scrapeNowHint}
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
            title={
              tab.key === "intel"
                ? t.tabIntelHint
                : tab.key === "suggestions"
                ? t.tabSuggestionsHint
                : t.plannerHint
            }
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
                  title={t.filterPlatformHint}
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
                  title={t.filterStatusHint}
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

      {activeTab === "calendar" && (
        <>
          <SectionDivider
            label={lang === "ar" ? `تقويم ${targetMonth}` : `Calendar ${targetMonth}`}
            isDark={isDark}
          />
          {calendarLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 mt-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <SkeletonCard key={i} isDark={isDark} />
              ))}
            </div>
          ) : calendarEntries.length === 0 ? (
            <div
              className={cn(
                "rounded-xl border p-12 mt-4 text-center",
                isDark ? "bg-slate-800/40 border-slate-700 text-slate-400" : "bg-gray-50 border-gray-200 text-gray-500"
              )}
            >
              {t.calendarEmpty}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 mt-4">
              {calendarEntries.map((item) => {
                const rawHooks = Array.isArray(item.five_hooks)
                  ? item.five_hooks
                  : typeof item.five_hooks === "string"
                  ? (() => {
                      try {
                        const parsed = JSON.parse(item.five_hooks);
                        return Array.isArray(parsed) ? parsed : [];
                      } catch {
                        return [];
                      }
                    })()
                  : [];

                const rawKeywords = Array.isArray(item.competitor_keywords)
                  ? item.competitor_keywords
                  : [];
                const rawHashtags = Array.isArray(item.recommended_hashtags)
                  ? item.recommended_hashtags
                  : [];

                const fullPackage = [
                  `Subject: ${item.subject_title || ""}`,
                  `Post Type: ${item.post_type || ""}`,
                  `Hooks: ${(rawHooks || []).join(" | ")}`,
                  `Instagram: ${item.content_instagram || ""}`,
                  `X: ${item.content_x || ""}`,
                  `TikTok: ${item.content_tiktok || ""}`,
                  `Facebook: ${item.content_facebook || ""}`,
                  `LinkedIn: ${item.content_linkedin || ""}`,
                  `Caption: ${item.caption_text || ""}`,
                  `Blog: ${item.blog_article || ""}`,
                  `Newsletter: ${item.newsletter_text || ""}`,
                  `Keywords: ${(rawKeywords || []).join(", ")}`,
                  `Hashtags: ${(rawHashtags || []).join(" ")}`,
                  `Banana image prompt: ${item.banana_image_prompt || ""}`,
                  `Video prompt: ${item.video_generator_prompt || ""}`,
                ].join("\n\n");

                return (
                  <div
                    key={item.id}
                    className={cn(
                      "rounded-xl border p-4 flex flex-col gap-3",
                      isDark ? "bg-slate-800 border-slate-700" : "bg-white border-gray-200"
                    )}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className={cn("text-xs px-2 py-0.5 rounded-full", isDark ? "bg-slate-700 text-slate-300" : "bg-gray-100 text-gray-600")}>{item.platform || "multi"}</span>
                      <span className={cn("text-xs", isDark ? "text-slate-500" : "text-gray-500")}>{item.publish_date || targetMonth}</span>
                    </div>
                    <h3 className={cn("font-semibold text-sm", isDark ? "text-white" : "text-gray-900")}>{item.subject_title || item.title_ar || item.title_en || "Untitled"}</h3>
                    <p className={cn("text-xs", isDark ? "text-slate-400" : "text-gray-600")}>{t.postType}: {item.post_type || "-"}</p>
                    {rawHooks.length > 0 && (
                      <ul className="space-y-1">
                        {rawHooks.slice(0, 5).map((hook, idx) => (
                          <li key={`${item.id}-hook-${idx}`} className={cn("text-xs", isDark ? "text-slate-300" : "text-gray-700")}>{idx + 1}. {hook}</li>
                        ))}
                      </ul>
                    )}
                    {rawKeywords.length > 0 && (
                      <p className={cn("text-xs", isDark ? "text-slate-400" : "text-gray-600")}>
                        {t.keywords}: {rawKeywords.join(", ")}
                      </p>
                    )}
                    {rawHashtags.length > 0 && (
                      <p className={cn("text-xs", isDark ? "text-slate-400" : "text-gray-600")}>
                        {t.hashtags}: {rawHashtags.join(" ")}
                      </p>
                    )}
                    <button
                      type="button"
                      onClick={() => navigator.clipboard.writeText(fullPackage)}
                      className={cn(
                        "mt-auto inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors",
                        isDark ? "bg-white/10 text-slate-200 hover:bg-white/15" : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      )}
                    >
                      <Copy size={12} />
                      {t.copyAll}
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}
