import { useMemo, useState } from "react";
import { useOutletContext } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  BarChart3,
  Bot,
  CheckCircle2,
  Clock3,
  ExternalLink,
  Filter,
  Mail,
  PlayCircle,
  Sparkles,
  TrendingUp,
  XCircle,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const REFRESH_MS = 5 * 60 * 1000;
const USD_TO_SAR = 3.75;

const metricCard = {
  padding: 18,
  borderRadius: 16,
  border: "1px solid rgba(255,255,255,0.14)",
  background: "linear-gradient(130deg, rgba(18,31,64,0.75), rgba(10,14,29,0.85))",
  boxShadow: "0 12px 35px rgba(0,0,0,0.25)",
};

function DashboardMetric({ icon: Icon, label, value, sub, color }) {
  return (
    <div style={metricCard}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
        <span style={{ color: "rgba(255,255,255,0.72)", fontSize: "0.82rem", letterSpacing: "0.05em", textTransform: "uppercase" }}>{label}</span>
        <div style={{ width: 34, height: 34, borderRadius: 9, display: "grid", placeItems: "center", background: `${color}22`, border: `1px solid ${color}55` }}>
          <Icon size={16} style={{ color }} />
        </div>
      </div>
      <div style={{ fontSize: "1.9rem", fontWeight: 800, lineHeight: 1.1 }}>{value}</div>
      <div style={{ marginTop: 6, fontSize: "0.86rem", color: "rgba(255,255,255,0.62)" }}>{sub}</div>
    </div>
  );
}

function fmtDate(v, lang) {
  if (!v) return "-";
  try {
    return new Date(v).toLocaleString(lang === "ar" ? "ar-SA" : "en-US");
  } catch {
    return v;
  }
}

function fmtCompact(num) {
  const n = Number(num || 0);
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return `${n}`;
}

export default function YouTubeTrendsDashboard() {
  const outlet = /** @type {{ lang?: string } | null} */ (useOutletContext());
  const lang = outlet.lang || "ar";
  const isRTL = lang === "ar";

  const t = useMemo(() => (
    lang === "ar"
      ? {
          subtitle: "لوحة ذكاء النمو",
          title: "منصة ذكاء إشارات النيتش",
          run: "التشغيل",
          updated: "آخر تحديث",
          autoRefresh: "تحديث تلقائي: 5 دقائق",
          refreshNow: "تحديث الآن",
          refreshCost: "تكلفة Apify للسحب",
          startScrape: "بدء سحب جديد",
          scraping: "جاري السحب...",
          sheet: "الجدول",
          slides: "الشرائح",
          loading: "جاري تحميل بيانات اللوحة...",
          errorTitle: "تعذر تحميل بيانات اللوحة",
          errorHint: "شغل scripts/export_youtube_dashboard_data.py لإنشاء app/public/niche-signal-intelligence-dashboard.json",
          channels: "القنوات",
          selected: "محددة في هذا التشغيل",
          scoredVideos: "الفيديوهات المقيمة",
          accepted: "فيديوهات مقبولة",
          rejected: "المرفوض",
          dropped: "مستبعد بسبب الصلة",
          acceptance: "نسبة القبول",
          keepRatio: "نسبة الاحتفاظ",
          runMomentum: "زخم التشغيل",
          signalSummary: "ملخص الإشارة",
          window: "النافذة",
          apiUnits: "وحدات API",
          runCost: "تكلفة Apify",
          to: "إلى",
          topChannels: "أفضل القنوات",
          channel: "القناة",
          category: "التصنيف",
          videos: "الفيديوهات",
          finalScore: "النتيجة النهائية",
          views: "المشاهدات",
          rejectSamples: "عينات الاستبعاد",
          rejectEmpty: "لا توجد عينات مستبعدة لهذا التشغيل.",
          unknownChannel: "قناة غير معروفة",
          rejectWord: "مرفوض",
          score: "النتيجة",
          topVideos: "أفضل الفيديوهات",
          trending: "رائج",
          trend: "الترند",
          insightsEn: "تحليلات (EN)",
          insightsAr: "تحليلات (AR)",
          noEn: "لا توجد ملاحظات إنجليزية حالياً.",
          noAr: "لا توجد ملاحظات عربية حالياً.",
          emailLabel: "آخر تقرير",
          emailDraft: "مسودة تم إنشاؤها",
          emailNone: "لم يُرسل بعد",
          emailTo: "إلى",
          emailDraftWarning: "يتم حفظ التقرير كمسودة في Gmail فقط — يجب إرساله يدوياً",
          wfLabel: "الورك فلو",
          wfActive: "مفعّل",
          sendReport: "إرسال التقرير",
          sending: "جاري الإرسال...",
          sent: "تم الإرسال ✓",
          sendError: "فشل الإرسال",
          chatPromptLabel: "رسالة التحليل",
          chatPlaceholder: "اكتب النيتش أو الطلب هنا...",
          chatResponse: "رد الوكيل",
          chatNoResponse: "لم يتم استلام رد نصي من الوكيل.",
          assistantTitle: "مساعد زيادة الذكي",
          assistantSubtitle: "اسأل وكيل الذكاء لتحليل النيتش وإشارات المحتوى الرائجة",
        }
      : {
          subtitle: "Ali Fallatah Growth Intelligence",
          title: "Niche Signal Intelligence Console",
          run: "Run",
          updated: "Updated",
          autoRefresh: "Auto refresh: 5m",
          refreshNow: "Refresh now",
          refreshCost: "Apify Scraping Cost",
          startScrape: "Start New Scrape",
          scraping: "Triggering...",
          sheet: "Sheet",
          slides: "Slides",
          loading: "Loading dashboard data...",
          errorTitle: "Cannot load dashboard payload",
          errorHint: "Run scripts/export_youtube_dashboard_data.py to generate app/public/niche-signal-intelligence-dashboard.json.",
          channels: "Channels",
          selected: "Selected this run",
          scoredVideos: "Scored Videos",
          accepted: "Accepted videos",
          rejected: "Rejected",
          dropped: "Dropped by relevance",
          acceptance: "Acceptance",
          keepRatio: "Keep ratio",
          runMomentum: "Run Momentum",
          signalSummary: "Signal Summary",
          window: "Window",
          apiUnits: "API Units",
          runCost: "Run Cost",
          to: "to",
          topChannels: "Top Channels",
          channel: "Channel",
          category: "Category",
          videos: "Videos",
          finalScore: "Final Score",
          views: "Views",
          rejectSamples: "Relevance Reject Samples",
          rejectEmpty: "No rejected sample saved yet for this run.",
          unknownChannel: "Unknown channel",
          rejectWord: "rejected",
          score: "score",
          topVideos: "Top Videos",
          trending: "Trending",
          trend: "Trend",
          insightsEn: "Insights (EN)",
          insightsAr: "Insights (AR)",
          noEn: "No English insight available.",
          noAr: "No Arabic insight available.",
          emailLabel: "Last Report",
          emailDraft: "Draft created",
          emailNone: "Not sent yet",
          emailTo: "to",
          emailDraftWarning: "Report is saved as a Gmail draft only — must be sent manually",
          wfLabel: "Workflow",
          wfActive: "Active",
          sendReport: "Send Report",
          sending: "Sending...",
          sent: "Sent ✓",
          sendError: "Send failed",
          chatPromptLabel: "Analysis prompt",
          chatPlaceholder: "Type the niche or request here...",
          chatResponse: "Agent response",
          chatNoResponse: "No text response received from agent.",
          assistantTitle: "Ziyada AI Helper",
          assistantSubtitle: "Ask our AI agent to analyze your niche and trending content signals",
        }
  ), [lang]);

  const { data, isLoading, isError, error, refetch, dataUpdatedAt } = useQuery({
    queryKey: ["niche_signal_intelligence_payload"],
    queryFn: async () => {
      const res = await fetch(`/niche-signal-intelligence-dashboard.json?ts=${Date.now()}`, { cache: "no-store" });
      if (!res.ok) throw new Error(`Dashboard data unavailable (${res.status})`);
      return res.json();
    },
    refetchInterval: REFRESH_MS,
    staleTime: 60_000,
  });

  const [scrapeState, setScrapeState] = useState("idle"); // idle | loading | done | error
  const [sendState, setSendState] = useState("idle"); // idle | sending | sent | error
  const [chatPrompt, setChatPrompt] = useState(
    lang === "ar"
      ? "ابحث عن ترندات يوتيوب في مجال الذكاء الاصطناعي والتسويق الرقمي"
      : "Find trending YouTube videos in AI automation and digital marketing",
  );
  const [chatReply, setChatReply] = useState("");

  async function sendReport(draftId) {
    setSendState("sending");
    try {
      const res = await fetch("/api/send-draft", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ draft_id: draftId }),
      });
      const json = await res.json();
      if (!res.ok || !json.ok) throw new Error(json.error || "Unknown error");
      setSendState("sent");
    } catch {
      setSendState("error");
      setTimeout(() => setSendState("idle"), 5000);
    }
  }

  async function triggerScrape() {
    const webhookUrl = import.meta.env.VITE_N8N_NSI_WEBHOOK || import.meta.env.VITE_N8N_YOUTUBE_WEBHOOK;
    if (!webhookUrl) {
      window.open("https://n8n.srv953562.hstgr.cloud", "_blank");
      return;
    }
    setScrapeState("loading");
    try {
      const prompt = String(chatPrompt || "").trim() || (
        lang === "ar"
          ? "ابحث عن ترندات يوتيوب في مجال الذكاء الاصطناعي والتسويق الرقمي"
          : "Find trending YouTube videos in AI automation and digital marketing"
      );
      const res = await fetch(webhookUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sessionId: "dashboard-trigger",
          action: "sendMessage",
          chatInput: prompt,
        }),
      });
      if (!res.ok) throw new Error(`n8n responded ${res.status}`);
      const json = await res.json().catch(() => ({}));
      const reply = json?.output || json?.text || "";
      setChatReply(reply || t.chatNoResponse);
      setScrapeState("done");
      setTimeout(() => setScrapeState("idle"), 4000);
    } catch {
      setChatReply("");
      setScrapeState("error");
      setTimeout(() => setScrapeState("idle"), 4000);
    }
  }

  const history = useMemo(() => (Array.isArray(data?.history) ? data.history : []), [data]);
  const runCostUsd = Number(data?.summary?.run_cost_usd || 0);
  const runCostSar = runCostUsd * USD_TO_SAR;

  return (
    <div className="trend-dashboard" dir={isRTL ? "rtl" : "ltr"} style={{ maxWidth: 1320, margin: "0 auto", padding: "30px 20px 44px" }}>
      <section
        className="glass-panel"
        style={{
          padding: "24px 22px",
          marginBottom: 18,
          borderRadius: 20,
          background:
            "radial-gradient(1200px 280px at -10% -20%, rgba(56,189,248,0.25), transparent 60%), radial-gradient(900px 260px at 100% -30%, rgba(34,197,94,0.22), transparent 60%), linear-gradient(140deg, rgba(12,20,44,0.9), rgba(8,10,24,0.95))",
        }}
      >
        <div style={{ display: "flex", gap: 16, alignItems: "center", justifyContent: "space-between", flexWrap: "wrap" }}>
          <div>
            <p style={{ color: "rgba(255,255,255,0.7)", fontSize: "0.82rem", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 8 }}>
              {t.subtitle}
            </p>
            <h1 style={{ fontSize: "clamp(1.4rem, 2.3vw, 2.25rem)", fontWeight: 900, lineHeight: 1.1, marginBottom: 10 }}>
              {t.title}
            </h1>
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", color: "rgba(255,255,255,0.78)", fontSize: "0.9rem" }}>
              <span style={{ display: "inline-flex", gap: 6, alignItems: "center" }}><Clock3 size={15} />{t.run}: {data?.summary?.run_id || "-"}</span>
              <span style={{ display: "inline-flex", gap: 6, alignItems: "center" }}><Activity size={15} />{t.updated}: {fmtDate(dataUpdatedAt || data?.generated_at_utc, lang)}</span>
              <span style={{ display: "inline-flex", gap: 6, alignItems: "center" }}><Filter size={15} />{t.autoRefresh}</span>
            </div>

            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 10, alignItems: "center" }}>
              {/* Email status */}
              <div style={{
                display: "inline-flex", gap: 6, alignItems: "center",
                padding: "5px 10px", borderRadius: 8,
                background: sendState === "sent" ? "rgba(74,222,128,0.12)" : data?.summary?.gmail_draft_id ? "rgba(251,191,36,0.12)" : "rgba(239,68,68,0.12)",
                border: `1px solid ${sendState === "sent" ? "rgba(74,222,128,0.4)" : data?.summary?.gmail_draft_id ? "rgba(251,191,36,0.4)" : "rgba(239,68,68,0.4)"}`,
                fontSize: "0.78rem", color: sendState === "sent" ? "#86efac" : data?.summary?.gmail_draft_id ? "#fde68a" : "#fca5a5",
              }}>
                <Mail size={13} />
                {t.emailLabel}: {sendState === "sent" ? t.sent : data?.summary?.gmail_draft_id ? t.emailDraft : t.emailNone}
                {data?.summary?.report_recipient ? ` → ${data.summary.report_recipient}` : ""}
              </div>

              {/* Send Report button — only when a draft exists and not yet sent */}
              {data?.summary?.gmail_draft_id && sendState !== "sent" ? (
                <button
                  onClick={() => sendReport(data.summary.gmail_draft_id)}
                  disabled={sendState === "sending"}
                  style={{
                    display: "inline-flex", gap: 6, alignItems: "center",
                    padding: "5px 12px", borderRadius: 8,
                    background: sendState === "error" ? "rgba(251,113,133,0.15)" : "rgba(56,189,248,0.14)",
                    border: `1px solid ${sendState === "error" ? "rgba(251,113,133,0.5)" : "rgba(56,189,248,0.4)"}`,
                    color: sendState === "error" ? "#fca5a5" : "#7dd3fc",
                    fontSize: "0.78rem", fontWeight: 700,
                    cursor: sendState === "sending" ? "not-allowed" : "pointer",
                    fontFamily: "inherit",
                    opacity: sendState === "sending" ? 0.7 : 1,
                  }}
                >
                  <Mail size={13} />
                  {sendState === "sending" ? t.sending : sendState === "error" ? t.sendError : t.sendReport}
                </button>
              ) : null}

              {/* Draft warning — only when unsent */}
              {data?.summary?.gmail_draft_id && sendState === "idle" ? (
                <div style={{
                  display: "inline-flex", gap: 5, alignItems: "center",
                  padding: "5px 10px", borderRadius: 8,
                  background: "rgba(251,191,36,0.08)",
                  border: "1px solid rgba(251,191,36,0.3)",
                  fontSize: "0.75rem", color: "rgba(253,230,138,0.85)",
                }}>
                  ⚠ {t.emailDraftWarning}
                </div>
              ) : null}

              {/* Workflow status */}
              <a
                href="https://n8n.srv953562.hstgr.cloud"
                target="_blank"
                rel="noreferrer"
                style={{
                  display: "inline-flex", gap: 6, alignItems: "center",
                  padding: "5px 10px", borderRadius: 8,
                  background: "rgba(74,222,128,0.1)",
                  border: "1px solid rgba(74,222,128,0.35)",
                  fontSize: "0.78rem", color: "#86efac",
                  textDecoration: "none",
                }}
              >
                <span style={{ width: 7, height: 7, borderRadius: "50%", background: "#4ade80", display: "inline-block" }} />
                {t.wfLabel}: {t.wfActive}
              </a>
            </div>
          </div>

          <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
            <div
              style={{
                minWidth: 290,
                flex: "1 1 420px",
                border: "1px solid rgba(56,189,248,0.35)",
                borderRadius: 14,
                background: "linear-gradient(145deg, rgba(2,132,199,0.18), rgba(30,41,59,0.45))",
                boxShadow: "0 0 0 1px rgba(56,189,248,0.15), 0 0 22px rgba(56,189,248,0.2)",
                padding: "10px 12px",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                <div
                  style={{
                    width: 30,
                    height: 30,
                    borderRadius: 10,
                    display: "grid",
                    placeItems: "center",
                    background: "radial-gradient(circle at 35% 30%, rgba(103,232,249,0.5), rgba(14,116,144,0.45))",
                    border: "1px solid rgba(125,211,252,0.7)",
                    boxShadow: "0 0 15px rgba(56,189,248,0.45)",
                    flexShrink: 0,
                  }}
                >
                  <Bot size={15} style={{ color: "#e0f2fe" }} />
                </div>
                <div>
                  <div style={{ fontSize: "0.84rem", fontWeight: 800, color: "#bae6fd" }}>{t.assistantTitle}</div>
                  <div style={{ fontSize: "0.74rem", color: "rgba(191,219,254,0.9)" }}>{t.assistantSubtitle}</div>
                </div>
              </div>

              <label style={{ display: "grid", gap: 4 }}>
                <span style={{ color: "rgba(255,255,255,0.74)", fontSize: "0.69rem", letterSpacing: "0.06em", textTransform: "uppercase" }}>{t.chatPromptLabel}</span>
                <input
                  type="text"
                  value={chatPrompt}
                  onChange={(e) => setChatPrompt(e.target.value)}
                  placeholder={t.chatPlaceholder}
                  style={{
                    border: "1px solid rgba(125,211,252,0.38)",
                    background: "rgba(15,23,42,0.55)",
                    color: "#fff",
                    borderRadius: 10,
                    padding: "9px 11px",
                    fontFamily: "inherit",
                  }}
                />
              </label>
            </div>

            <div style={{ textAlign: isRTL ? "right" : "left", lineHeight: 1.3 }}>
              <div style={{ color: "#fde68a", fontSize: "0.76rem", fontWeight: 700 }}>{t.refreshCost}</div>
              <div style={{ color: "rgba(255,255,255,0.8)", fontSize: "0.77rem" }}>${runCostUsd.toFixed(2)} | {runCostSar.toFixed(2)} ر.س</div>
            </div>

            <button
              onClick={() => refetch()}
              style={{
                border: "1px solid rgba(255,255,255,0.22)",
                background: "rgba(255,255,255,0.08)",
                color: "#fff",
                borderRadius: 12,
                padding: "9px 14px",
                fontWeight: 700,
                cursor: "pointer",
                fontFamily: "inherit",
              }}
            >
              {t.refreshNow}
            </button>

            <button
              onClick={triggerScrape}
              disabled={scrapeState === "loading"}
              style={{
                border: scrapeState === "done" ? "1px solid rgba(74,222,128,0.6)" : scrapeState === "error" ? "1px solid rgba(251,113,133,0.6)" : "1px solid rgba(251,191,36,0.5)",
                background: scrapeState === "done" ? "rgba(74,222,128,0.15)" : scrapeState === "error" ? "rgba(251,113,133,0.15)" : "rgba(251,191,36,0.12)",
                color: scrapeState === "done" ? "#86efac" : scrapeState === "error" ? "#fca5a5" : "#fde68a",
                borderRadius: 12,
                padding: "9px 14px",
                fontWeight: 700,
                cursor: scrapeState === "loading" ? "not-allowed" : "pointer",
                fontFamily: "inherit",
                display: "inline-flex",
                gap: 7,
                alignItems: "center",
                direction: "ltr",
                opacity: scrapeState === "loading" ? 0.7 : 1,
              }}
            >
              <PlayCircle size={15} />
              {scrapeState === "loading" ? t.scraping : scrapeState === "done" ? "✓" : scrapeState === "error" ? "✗" : t.startScrape}
            </button>

            {data?.summary?.sheet_url ? (
              <a
                href={data.summary.sheet_url}
                target="_blank"
                rel="noreferrer"
                style={{ border: "1px solid rgba(22,163,74,0.5)", background: "rgba(22,163,74,0.18)", color: "#dcfce7", borderRadius: 12, padding: "9px 14px", fontWeight: 700, display: "inline-flex", gap: 7, alignItems: "center" }}
              >
                {t.sheet} <ExternalLink size={14} />
              </a>
            ) : null}

            {data?.summary?.deck_url ? (
              <a
                href={data.summary.deck_url}
                target="_blank"
                rel="noreferrer"
                style={{ border: "1px solid rgba(59,130,246,0.55)", background: "rgba(59,130,246,0.2)", color: "#dbeafe", borderRadius: 12, padding: "9px 14px", fontWeight: 700, display: "inline-flex", gap: 7, alignItems: "center" }}
              >
                {t.slides} <ExternalLink size={14} />
              </a>
            ) : null}
          </div>
        </div>

        {chatReply ? (
          <div style={{ marginTop: 12, padding: "11px 12px", borderRadius: 12, border: "1px solid rgba(56,189,248,0.35)", background: "rgba(2,132,199,0.1)" }}>
            <div style={{ fontSize: "0.72rem", textTransform: "uppercase", letterSpacing: "0.06em", color: "#7dd3fc", marginBottom: 6 }}>{t.chatResponse}</div>
            <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.5, fontSize: "0.9rem" }}>{chatReply}</div>
          </div>
        ) : null}
      </section>

      {isLoading ? (
        <div className="glass-panel" style={{ padding: 32, borderRadius: 16 }}>
          <p style={{ opacity: 0.8 }}>{t.loading}</p>
        </div>
      ) : null}

      {isError ? (
        <div className="glass-panel" style={{ padding: 32, borderRadius: 16, border: "1px solid rgba(239,68,68,0.4)", background: "rgba(127,29,29,0.35)" }}>
          <h3 style={{ marginBottom: 10, fontSize: "1.05rem" }}>{t.errorTitle}</h3>
          <p style={{ opacity: 0.86, marginBottom: 8 }}>{String(error?.message || "Unknown error")}</p>
          <p style={{ opacity: 0.7, fontSize: "0.9rem" }}>{t.errorHint}</p>
        </div>
      ) : null}

      {!isLoading && !isError && data ? (
        <>
          <section className="trend-metrics-grid" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))", gap: 14, marginBottom: 18 }}>
            <DashboardMetric icon={BarChart3} label={t.channels} value={data.kpis?.channels_selected || 0} sub={t.selected} color="#22d3ee" />
            <DashboardMetric icon={PlayCircle} label={t.scoredVideos} value={data.kpis?.videos_scored || 0} sub={t.accepted} color="#60a5fa" />
            <DashboardMetric icon={XCircle} label={t.rejected} value={data.kpis?.videos_rejected || 0} sub={t.dropped} color="#fb7185" />
            <DashboardMetric icon={CheckCircle2} label={t.acceptance} value={`${data.kpis?.acceptance_rate || 0}%`} sub={t.keepRatio} color="#4ade80" />
          </section>

          <section className="trend-summary-grid" style={{ display: "grid", gridTemplateColumns: "minmax(0, 1.2fr) minmax(0, 0.8fr)", gap: 14, marginBottom: 18 }}>
            <div className="glass-panel" style={{ padding: 16, borderRadius: 16 }}>
              <h3 style={{ fontSize: "1rem", marginBottom: 12 }}>{t.runMomentum}</h3>
              <div style={{ width: "100%", height: 240 }}>
                <ResponsiveContainer>
                  <AreaChart data={history} margin={{ left: 4, right: 10, top: 8, bottom: 0 }}>
                    <defs>
                      <linearGradient id="scoredFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.05} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.12)" />
                    <XAxis dataKey="run_id" tick={{ fill: "rgba(255,255,255,0.7)", fontSize: 11 }} axisLine={{ stroke: "rgba(255,255,255,0.15)" }} tickLine={false} />
                    <YAxis tick={{ fill: "rgba(255,255,255,0.7)", fontSize: 11 }} axisLine={{ stroke: "rgba(255,255,255,0.15)" }} tickLine={false} />
                    <Tooltip
                      contentStyle={{
                        background: "rgba(8,16,30,0.95)",
                        border: "1px solid rgba(56,189,248,0.4)",
                        borderRadius: 10,
                      }}
                      labelStyle={{ color: "#e2e8f0" }}
                    />
                    <Area type="monotone" dataKey="videos_scored" stroke="#38bdf8" strokeWidth={2.4} fill="url(#scoredFill)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="glass-panel" style={{ padding: 16, borderRadius: 16 }}>
              <h3 style={{ fontSize: "1rem", marginBottom: 12 }}>{t.signalSummary}</h3>
              <div style={{ display: "grid", gap: 12 }}>
                <div style={{ padding: "11px 12px", border: "1px solid rgba(255,255,255,0.13)", borderRadius: 12 }}>
                  <p style={{ fontSize: "0.75rem", color: "rgba(255,255,255,0.65)", textTransform: "uppercase", letterSpacing: "0.06em" }}>{t.window}</p>
                  <p style={{ marginTop: 5, fontWeight: 700 }}>{fmtDate(data.summary?.week_start, lang)} {t.to} {fmtDate(data.summary?.week_end, lang)}</p>
                </div>
                <div style={{ padding: "11px 12px", border: "1px solid rgba(255,255,255,0.13)", borderRadius: 12 }}>
                  <p style={{ fontSize: "0.75rem", color: "rgba(255,255,255,0.65)", textTransform: "uppercase", letterSpacing: "0.06em" }}>{t.apiUnits}</p>
                  <p style={{ marginTop: 5, fontWeight: 700 }}>{fmtCompact(data.summary?.api_units_est || 0)}</p>
                </div>
                <div style={{ padding: "11px 12px", border: "1px solid rgba(255,255,255,0.13)", borderRadius: 12 }}>
                  <p style={{ fontSize: "0.75rem", color: "rgba(255,255,255,0.65)", textTransform: "uppercase", letterSpacing: "0.06em" }}>{t.runCost}</p>
                  <p style={{ marginTop: 5, fontWeight: 700 }}>${runCostUsd.toFixed(2)} | {runCostSar.toFixed(2)} ر.س</p>
                </div>
              </div>
            </div>
          </section>

          <section className="trend-split-grid" style={{ display: "grid", gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1fr)", gap: 14, marginBottom: 18 }}>
            <div className="glass-panel" style={{ padding: 16, borderRadius: 16, overflow: "auto" }}>
              <h3 style={{ fontSize: "1rem", marginBottom: 10 }}>{t.topChannels}</h3>
              <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 540 }}>
                <thead>
                  <tr>
                    {["#", t.channel, t.category, t.videos, t.finalScore, t.views].map((h) => (
                      <th key={h} style={{ textAlign: "left", fontSize: "0.74rem", color: "rgba(255,255,255,0.7)", borderBottom: "1px solid rgba(255,255,255,0.12)", padding: "8px 9px", letterSpacing: "0.06em", textTransform: "uppercase" }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(data.top_channels || []).slice(0, 10).map((c, i) => (
                    <tr key={`${c.channel_id || c.channel_title}-${i}`}>
                      <td style={{ padding: "9px", borderBottom: "1px solid rgba(255,255,255,0.06)", fontWeight: 700 }}>{i + 1}</td>
                      <td style={{ padding: "9px", borderBottom: "1px solid rgba(255,255,255,0.06)", fontWeight: 600 }}>{c.channel_title || "-"}</td>
                      <td style={{ padding: "9px", borderBottom: "1px solid rgba(255,255,255,0.06)", opacity: 0.82 }}>{c.category_label || "-"}</td>
                      <td style={{ padding: "9px", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>{c.video_count || 0}</td>
                      <td style={{ padding: "9px", borderBottom: "1px solid rgba(255,255,255,0.06)", color: "#86efac", fontWeight: 700 }}>{Number(c.final_channel_score || 0).toFixed(1)}</td>
                      <td style={{ padding: "9px", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>{fmtCompact(c.sum_views || 0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="glass-panel" style={{ padding: 16, borderRadius: 16 }}>
              <h3 style={{ fontSize: "1rem", marginBottom: 10 }}>{t.rejectSamples}</h3>
              <div style={{ display: "grid", gap: 8 }}>
                {(data.rejected_samples || []).length === 0 ? (
                  <p style={{ opacity: 0.7, paddingTop: 10 }}>{t.rejectEmpty}</p>
                ) : (
                  (data.rejected_samples || []).slice(0, 6).map((v, i) => (
                    <div key={`${v.video_id || i}`} style={{ padding: "11px 12px", border: "1px solid rgba(251,113,133,0.33)", borderRadius: 12, background: "rgba(127,29,29,0.2)" }}>
                      <div style={{ fontWeight: 700, fontSize: "0.91rem", marginBottom: 6 }}>{v.title || "-"}</div>
                      <div style={{ fontSize: "0.8rem", opacity: 0.76, marginBottom: 4 }}>{v.channel_title || t.unknownChannel}</div>
                      <div style={{ fontSize: "0.8rem", color: "#fecaca" }}>
                        {v.relevance_reason || t.rejectWord} ({t.score}: {Number(v.relevance_score || 0).toFixed(2)})
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </section>

          <section className="glass-panel trend-videos-panel" style={{ padding: 16, borderRadius: 16, marginBottom: 18 }}>
            <h3 style={{ fontSize: "1rem", marginBottom: 10 }}>{t.topVideos}</h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: 10 }}>
              {(data.top_videos || []).slice(0, 8).map((v, i) => (
                <article key={`${v.video_id || i}`} style={{ border: "1px solid rgba(255,255,255,0.12)", borderRadius: 12, padding: 12, background: "rgba(255,255,255,0.03)" }}>
                  <p style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: "0.73rem", color: "#7dd3fc", marginBottom: 6 }}>
                    <TrendingUp size={13} />#{i + 1} {t.trending}
                  </p>
                  <h4 style={{ fontSize: "0.96rem", lineHeight: 1.35, marginBottom: 8 }}>{v.title || "-"}</h4>
                  <p style={{ fontSize: "0.82rem", opacity: 0.8, marginBottom: 8 }}>{v.channel_title || t.unknownChannel}</p>
                  <div style={{ display: "flex", justifyContent: "space-between", gap: 10, fontSize: "0.8rem" }}>
                    <span>{t.views}: <strong>{fmtCompact(v.views || 0)}</strong></span>
                    <span>{t.trend}: <strong style={{ color: "#a7f3d0" }}>{Number(v.trend_score || 0).toFixed(1)}</strong></span>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="trend-split-grid" style={{ display: "grid", gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1fr)", gap: 14 }}>
            <div className="glass-panel" style={{ padding: 16, borderRadius: 16 }}>
              <h3 style={{ fontSize: "1rem", marginBottom: 10, display: "inline-flex", alignItems: "center", gap: 8 }}><Sparkles size={16} />{t.insightsEn}</h3>
              <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit", lineHeight: 1.6, fontSize: "0.9rem", opacity: 0.9 }}>{data.insights_en || t.noEn}</pre>
            </div>
            <div className="glass-panel" style={{ padding: 16, borderRadius: 16 }}>
              <h3 style={{ fontSize: "1rem", marginBottom: 10, display: "inline-flex", alignItems: "center", gap: 8 }}><Sparkles size={16} />{t.insightsAr}</h3>
              <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit", lineHeight: 1.7, fontSize: "0.9rem", opacity: 0.93 }}>{data.insights_ar || t.noAr}</pre>
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}
