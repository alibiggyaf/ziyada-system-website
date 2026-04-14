import { useState, useRef, useEffect } from "react";
import { useOutletContext, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { siteApi } from "@/api/siteApi";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import StatCard from "@/admin/components/StatCard";
import DataTable from "@/admin/components/DataTable";
import StatusBadge from "@/admin/components/StatusBadge";
import {
  Users,
  Calendar,
  FileText,
  Mail,
  Plus,
  Eye,
  Send,
  Loader2,
  Bot,
  Sparkles,
  Zap,
} from "lucide-react";
import { format } from "date-fns";

/* ================================================================== */
/*  Bilingual labels                                                   */
/* ================================================================== */
const L = {
  ar: {
    title: "لوحة التحكم",
    subtitle: "نظرة عامة على زيادة سيستم",
    totalLeads: "إجمالي العملاء المحتملين",
    bookingsToday: "حجوزات اليوم",
    publishedPosts: "المقالات المنشورة",
    activeSubscribers: "المشتركون النشطون",
    recentLeads: "آخر العملاء المحتملين",
    recentBookings: "آخر الحجوزات",
    quickActions: "إجراءات سريعة",
    newPost: "مقال جديد",
    ziyadaWriter: "عميل زيادة الذكي",
    ziyadaWriterPlaceholder: "أدخل موضوع البحث أو ألصق بيانات المنافسين...",
    ziyadaWriterSend: "بحث وتوليد",
    ziyadaWriterSuccess: "تم تفعيل سير العمل! تحقق من مسودة Gmail خلال دقيقتين.",
    ziyadaWriterError: "فشل تفعيل العميل.",
    viewAllLeads: "عرض جميع العملاء",
    aiAgent: "عميل ذكي",
    aiPlaceholder: "اكتب رسالتك للمساعد...",
    aiSend: "إرسال",
    aiEmpty: "اسأل المساعد الذكي أي شيء عن النظام...",
    aiError: "حدث خطأ. حاول مرة أخرى.",
    name: "الاسم",
    email: "البريد",
    source: "المصدر",
    status: "الحالة",
    date: "التاريخ",
    time: "الوقت",
    noLeads: "لا يوجد عملاء محتملين بعد",
    noBookings: "لا يوجد حجوزات بعد",
  },
  en: {
    title: "Dashboard",
    subtitle: "Ziyada Systems overview",
    totalLeads: "Total Leads",
    bookingsToday: "Bookings Today",
    publishedPosts: "Published Posts",
    activeSubscribers: "Active Subscribers",
    recentLeads: "Recent Leads",
    recentBookings: "Recent Bookings",
    quickActions: "Quick Actions",
    newPost: "New Blog Post",
    ziyadaWriter: "Ziyada Writer Agent",
    ziyadaWriterPlaceholder: "Enter search topic or paste competitor intel...",
    ziyadaWriterSend: "Search & Generate",
    ziyadaWriterSuccess: "Workflow triggered! Check your Gmail draft in 2 mins.",
    ziyadaWriterError: "Failed to trigger agent.",
    viewAllLeads: "View All Leads",
    aiAgent: "AI Agent",
    aiPlaceholder: "Type a message for the assistant...",
    aiSend: "Send",
    aiEmpty: "Ask the AI assistant anything about the system...",
    aiError: "Error occurred. Try again.",
    name: "Name",
    email: "Email",
    source: "Source",
    status: "Status",
    date: "Date",
    time: "Time",
    noLeads: "No leads yet",
    noBookings: "No bookings yet",
  },
};

/* ================================================================== */
/*  Session ID for AI chat                                             */
/* ================================================================== */
function getSessionId() {
  const key = "ziyada_admin_chat_session";
  let id = sessionStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem(key, id);
  }
  return id;
}

/* ================================================================== */
/*  DashboardHome                                                      */
/* ================================================================== */
export default function DashboardHome() {
  const { lang = "ar", theme = "dark" } = useOutletContext() || {};
  const t = L[lang] || L.ar;
  const isDark = theme === "dark";
  const isRTL = lang === "ar";

  /* ---- Data queries ---- */
  const { data: leads = [], isLoading: loadingLeads } = useQuery({
    queryKey: ["admin-leads"],
    queryFn: () => siteApi.entities.Lead.list("-created_at", 100),
  });

  const { data: bookings = [], isLoading: loadingBookings } = useQuery({
    queryKey: ["admin-bookings"],
    queryFn: () => siteApi.entities.Booking.list("-created_at", 100),
  });

  const { data: posts = [], isLoading: loadingPosts } = useQuery({
    queryKey: ["admin-posts"],
    queryFn: () => siteApi.entities.BlogPost.list("-created_at", 100),
  });

  const { data: subscribers = [], isLoading: loadingSubs } = useQuery({
    queryKey: ["admin-subscribers"],
    queryFn: () => siteApi.entities.Subscriber.list("-created_at", 100),
  });

  /* ---- Derived data ---- */
  const todayStr = format(new Date(), "yyyy-MM-dd");
  const bookingsToday = bookings.filter((b) => b.booking_date === todayStr);
  const publishedPosts = posts.filter((p) => p.status === "published");
  const activeSubs = subscribers.filter((s) => s.status === "active");
  const recentLeads = leads.slice(0, 5);
  const recentBookings = bookings.slice(0, 5);

  /* ---- AI Chat state ---- */
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef(null);
  const webhookUrl = import.meta.env.VITE_CHATBOT_WEBHOOK;

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages, chatLoading]);

  const sendChat = async () => {
    const text = chatInput.trim();
    if (!text || chatLoading) return;

    setChatMessages((prev) => [...prev, { role: "user", content: text }]);
    setChatInput("");
    setChatLoading(true);

    try {
      const res = await fetch(webhookUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "sendMessage",
          chatInput: text,
          sessionId: getSessionId(),
        }),
      });

      const data = await res.json();
      let reply =
        data.output ||
        data.text ||
        data.response ||
        data.message ||
        data.choices?.[0]?.message?.content ||
        data.content ||
        "No response";

      reply = String(reply).trim() || "No response";
      setChatMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch {
      setChatMessages((prev) => [
        ...prev,
        { role: "assistant", content: t.aiError },
      ]);
    }
    setChatLoading(false);
  };

  /* ---- Ziyada Writer Agent ---- */
  const [writerInput, setWriterInput] = useState("");
  const [writerLoading, setWriterLoading] = useState(false);

  const triggerWriter = async () => {
    const text = writerInput.trim();
    if (!text || writerLoading) return;

    setWriterLoading(true);
    try {
      await siteApi.functions.triggerZiyadaWriter(text);
      toast.success(t.ziyadaWriterSuccess);
      setWriterInput("");
    } catch (err) {
      console.error(err);
      toast.error(t.ziyadaWriterError);
    } finally {
      setWriterLoading(false);
    }
  };

  /* ---- Table columns ---- */
  const leadColumns = [
    { key: "name", label: t.name, render: (_, r) => r.name || "\u2014" },
    { key: "email", label: t.email },
    {
      key: "source",
      label: t.source,
      render: (_, r) => <StatusBadge status={r.source} lang={lang} />,
    },
    {
      key: "status",
      label: t.status,
      render: (_, r) => <StatusBadge status={r.status} lang={lang} />,
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
  ];

  const bookingColumns = [
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
    { key: "booking_date", label: t.date },
    { key: "booking_time", label: t.time },
    {
      key: "status",
      label: t.status,
      render: (_, r) => <StatusBadge status={r.status} lang={lang} />,
    },
  ];

  return (
    <div className="max-w-7xl mx-auto" dir={isRTL ? "rtl" : "ltr"}>
      {/* ---- Header ---- */}
      <div className="mb-8">
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

      {/* ---- Stat Cards ---- */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          title={t.totalLeads}
          value={leads.length}
          icon={Users}
          color="blue"
          loading={loadingLeads}
          theme={theme}
        />
        <StatCard
          title={t.bookingsToday}
          value={bookingsToday.length}
          icon={Calendar}
          color="green"
          loading={loadingBookings}
          theme={theme}
        />
        <StatCard
          title={t.publishedPosts}
          value={publishedPosts.length}
          icon={FileText}
          color="purple"
          loading={loadingPosts}
          theme={theme}
        />
        <StatCard
          title={t.activeSubscribers}
          value={activeSubs.length}
          icon={Mail}
          color="amber"
          loading={loadingSubs}
          theme={theme}
        />
      </div>

      {/* ---- Recent Tables (two columns) ---- */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Recent Leads */}
        <div>
          <h2
            className={cn(
              "text-lg font-bold mb-3",
              isDark ? "text-white" : "text-gray-900"
            )}
          >
            {t.recentLeads}
          </h2>
          {loadingLeads ? (
            <div
              className={cn(
                "rounded-xl border p-8 flex justify-center",
                isDark
                  ? "bg-slate-800/60 border-white/10"
                  : "bg-white border-gray-200"
              )}
            >
              <Loader2 className="animate-spin text-blue-500" size={24} />
            </div>
          ) : (
            <DataTable
              columns={leadColumns}
              data={recentLeads}
              theme={theme}
              lang={lang}
              emptyMessage={t.noLeads}
            />
          )}
        </div>

        {/* Recent Bookings */}
        <div>
          <h2
            className={cn(
              "text-lg font-bold mb-3",
              isDark ? "text-white" : "text-gray-900"
            )}
          >
            {t.recentBookings}
          </h2>
          {loadingBookings ? (
            <div
              className={cn(
                "rounded-xl border p-8 flex justify-center",
                isDark
                  ? "bg-slate-800/60 border-white/10"
                  : "bg-white border-gray-200"
              )}
            >
              <Loader2 className="animate-spin text-green-500" size={24} />
            </div>
          ) : (
            <DataTable
              columns={bookingColumns}
              data={recentBookings}
              theme={theme}
              lang={lang}
              emptyMessage={t.noBookings}
            />
          )}
        </div>
      </div>

      {/* ---- Quick Actions ---- */}
      <div className="mb-8">
        <h2
          className={cn(
            "text-lg font-bold mb-3",
            isDark ? "text-white" : "text-gray-900"
          )}
        >
          {t.quickActions}
        </h2>
        <div className="flex flex-wrap gap-3">
          <Link
            to="/admin/blog/new"
            className={cn(
              "inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold transition-colors",
              "bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700"
            )}
          >
            <Plus size={16} /> {t.newPost}
          </Link>
          <Link
            to="/admin/leads"
            className={cn(
              "inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold transition-colors",
              isDark
                ? "bg-white/10 text-white hover:bg-white/15"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            )}
          >
            <Eye size={16} /> {t.viewAllLeads}
          </Link>
        </div>
      </div>

      {/* ---- Ziyada Writer Agent Section ---- */}
      <div className="mb-8">
        <h2
          className={cn(
            "text-lg font-bold mb-3 flex items-center gap-2",
            isDark ? "text-white" : "text-gray-900"
          )}
        >
          <Sparkles size={20} className="text-blue-500" />
          {t.ziyadaWriter}
        </h2>
        <div
          className={cn(
            "rounded-xl border overflow-hidden p-4",
            isDark
              ? "bg-slate-800/60 border-white/10"
              : "bg-white border-gray-200 shadow-sm"
          )}
        >
          <div className="space-y-4">
            <textarea
              value={writerInput}
              onChange={(e) => setWriterInput(e.target.value)}
              placeholder={t.ziyadaWriterPlaceholder}
              rows={4}
              className={cn(
                "w-full px-4 py-3 rounded-xl text-sm transition-all focus:ring-2 focus:ring-blue-500 outline-none resize-none",
                isDark
                  ? "bg-white/5 border-white/10 text-white placeholder-gray-500"
                  : "bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-400"
              )}
            />
            <div className="flex justify-end">
              <button
                onClick={triggerWriter}
                disabled={writerLoading || !writerInput.trim()}
                className={cn(
                  "inline-flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-bold transition-all disabled:opacity-50",
                  "bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700"
                )}
              >
                {writerLoading ? (
                  <Loader2 className="animate-spin" size={18} />
                ) : (
                  <Zap size={18} />
                )}
                {t.ziyadaWriterSend}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* ---- AI Agent Chat Box ---- */}
      <div className="mb-8">
        <h2
          className={cn(
            "text-lg font-bold mb-3 flex items-center gap-2",
            isDark ? "text-white" : "text-gray-900"
          )}
        >
          <Bot size={20} className="text-purple-500" />
          {t.aiAgent}
        </h2>
        <div
          className={cn(
            "rounded-xl border overflow-hidden",
            isDark
              ? "bg-slate-800/60 border-white/10"
              : "bg-white border-gray-200 shadow-sm"
          )}
        >
          {/* Messages area */}
          <div className="max-h-64 overflow-y-auto p-4 space-y-3">
            {chatMessages.length === 0 && (
              <p
                className={cn(
                  "text-sm text-center py-4",
                  isDark ? "text-gray-500" : "text-gray-400"
                )}
              >
                {t.aiEmpty}
              </p>
            )}
            {chatMessages.map((msg, i) => (
              <div
                key={i}
                className={cn(
                  "flex",
                  msg.role === "user" ? "justify-end" : "justify-start"
                )}
              >
                <div
                  className={cn(
                    "max-w-[80%] rounded-xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap",
                    msg.role === "user"
                      ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white"
                      : isDark
                      ? "bg-white/10 text-gray-200"
                      : "bg-gray-100 text-gray-800"
                  )}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {chatLoading && (
              <div className="flex justify-start">
                <div
                  className={cn(
                    "rounded-xl px-4 py-2.5",
                    isDark ? "bg-white/10" : "bg-gray-100"
                  )}
                >
                  <Loader2 size={16} className="animate-spin text-purple-500" />
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input bar */}
          <div
            className={cn(
              "flex items-center gap-2 px-4 py-3 border-t",
              isDark ? "border-white/10" : "border-gray-100"
            )}
          >
            <input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendChat()}
              placeholder={t.aiPlaceholder}
              disabled={chatLoading}
              className={cn(
                "flex-1 bg-transparent text-sm outline-none",
                isDark
                  ? "text-white placeholder:text-gray-500"
                  : "text-gray-900 placeholder:text-gray-400"
              )}
              dir={isRTL ? "rtl" : "ltr"}
            />
            <button
              onClick={sendChat}
              disabled={!chatInput.trim() || chatLoading}
              className={cn(
                "rounded-lg p-2 transition-colors disabled:opacity-40",
                chatInput.trim()
                  ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white"
                  : isDark
                  ? "text-gray-600"
                  : "text-gray-400"
              )}
            >
              <Send size={16} className={isRTL ? "rotate-180" : ""} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
