import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageCircle, X, Send, Loader2 } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

const L = {
  ar: {
    name: "مساعد زيادة",
    role: "مستشار أعمال رقمي",
    welcome: "أهلاً! أنا مساعد زيادة سيستم. كيف أقدر أساعدك اليوم؟",
    placeholder: "اكتب رسالتك...",
    quickReplies: [
      { label: "خدماتنا", value: "وش خدماتكم؟" },
      { label: "احجز استشارة", value: "أبي أحجز استشارة مجانية" },
      { label: "اطلب عرض سعر", value: "أبي عرض سعر" },
    ],
    offline: "المساعد غير متاح حالياً. تقدر تحجز استشارة مجانية أو تتواصل معنا مباشرة.",
    offlineCta: "احجز استشارة مجانية",
    error: "عذراً، حصل خطأ. حاول مرة ثانية.",
  },
  en: {
    name: "Ziyada Assistant",
    role: "Digital Business Consultant",
    welcome: "Hi! I'm the Ziyada Systems assistant. How can I help you today?",
    placeholder: "Type your message...",
    quickReplies: [
      { label: "Our Services", value: "What are your services?" },
      { label: "Book Consultation", value: "I'd like to book a free consultation" },
      { label: "Get a Quote", value: "I need a price quote" },
    ],
    offline: "The assistant is currently unavailable. You can book a free consultation or contact us directly.",
    offlineCta: "Book Free Consultation",
    error: "Sorry, something went wrong. Please try again.",
  },
};

export default function FloatingChatWidget({ lang = "ar", theme = "dark" }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [offline, setOffline] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);
  const isRTL = lang === "ar";
  const l = L[lang] || L.ar;

  const webhookUrl = import.meta.env.VITE_CHATBOT_WEBHOOK;
  const enabled = import.meta.env.VITE_CHATBOT_ENABLED !== "false";

  useEffect(() => {
    if (open && messages.length === 0) {
      setMessages([{ role: "assistant", content: l.welcome }]);
    }
  }, [open]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (open && inputRef.current) {
      inputRef.current.focus();
    }
  }, [open]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    const userMsg = { role: "user", content: text.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    if (!webhookUrl) {
      setOffline(true);
      setLoading(false);
      return;
    }

    try {
      const res = await fetch(webhookUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "sendMessage",
          chatInput: text.trim(),
          sessionId: getSessionId(),
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        const errMsg = errData?.message || l.error;
        setMessages((prev) => [...prev, { role: "assistant", content: errMsg }]);
        setLoading(false);
        return;
      }
      const data = await res.json();
      // Support multiple response formats: Gemini Flash, OpenAI, Claude, etc.
      let reply = data.output ||
                  data.text ||
                  data.response ||
                  data.message ||
                  data.choices?.[0]?.message?.content ||
                  data.choices?.[0]?.text ||
                  data.content ||
                  l.offline;

      // Ensure reply is a string
      reply = String(reply).trim() || l.offline;

      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((prev) => [...prev, { role: "assistant", content: l.error }]);
    }
    setLoading(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  if (!enabled) return null;

  return (
    <>
      {/* Floating button with glow + label */}
      <AnimatePresence>
        {!open && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
            className="fixed z-50 flex items-center gap-2 chat-widget-trigger"
            style={{
              bottom: 24,
              right: isRTL ? 24 : "auto",
              left: isRTL ? "auto" : 24,
              direction: "ltr",
              flexDirection: isRTL ? "row-reverse" : "row",
            }}
          >
            {/* Title label */}
            <motion.div
              initial={{ opacity: 0, x: isRTL ? 10 : -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5, duration: 0.4 }}
              className="rounded-full px-3 py-1.5 text-xs font-bold whitespace-nowrap chat-widget-label"
              style={{
                background: theme === "dark" ? "rgba(15,23,42,0.85)" : "rgba(255,255,255,0.92)",
                color: "#7c3aed",
                border: "1px solid rgba(124,58,237,0.3)",
                backdropFilter: "blur(12px)",
                boxShadow: "0 2px 12px rgba(124,58,237,0.15)",
              }}
            >
              {isRTL ? "مساعد زيادة الذكي" : "Ziyada AI Assistant"}
            </motion.div>

            {/* Glowing button */}
            <button
              onClick={() => setOpen(true)}
              className={cn(
                "relative flex items-center justify-center rounded-full",
                "w-14 h-14 hover:scale-110 transition-transform cursor-pointer"
              )}
              style={{
                background: "linear-gradient(135deg, #3b82f6, #7c3aed)",
                color: "#fff",
                boxShadow: "0 0 20px rgba(124,58,237,0.5), 0 0 40px rgba(59,130,246,0.3), 0 4px 16px rgba(0,0,0,0.2)",
                animation: "chatGlow 2s ease-in-out infinite",
              }}
            >
              <MessageCircle size={26} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Glow keyframes */}
      <style>{`
        @keyframes chatGlow {
          0%, 100% { box-shadow: 0 0 20px rgba(124,58,237,0.5), 0 0 40px rgba(59,130,246,0.3), 0 4px 16px rgba(0,0,0,0.2); }
          50% { box-shadow: 0 0 30px rgba(124,58,237,0.7), 0 0 60px rgba(59,130,246,0.4), 0 4px 20px rgba(0,0,0,0.3); }
        }
        @media (max-width: 768px) {
          .chat-widget-trigger { bottom: 80px !important; }
          .chat-widget-label { display: none !important; }
        }
      `}</style>

      {/* Chat panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="fixed z-50 flex flex-col overflow-hidden rounded-2xl shadow-2xl"
            dir={isRTL ? "rtl" : "ltr"}
            style={{
              width: 380,
              maxWidth: "calc(100vw - 32px)",
              height: 520,
              maxHeight: "calc(100vh - 100px)",
              bottom: 24,
              right: isRTL ? 24 : "auto",
              left: isRTL ? "auto" : 24,
              background: theme === "dark" ? "#0f172a" : "#ffffff",
              border: `1px solid ${theme === "dark" ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)"}`,
            }}
          >
            {/* Header */}
            <div
              className="flex items-center gap-3 px-4 py-3"
              style={{
                background: "linear-gradient(135deg, #1e3a8a, #7c3aed)",
                color: "#fff",
              }}
            >
              <Avatar className="h-9 w-9">
                <AvatarFallback style={{ background: "rgba(255,255,255,0.2)", color: "#fff", fontWeight: 700, fontSize: "0.8rem" }}>
                  ز
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <div className="font-bold text-sm leading-tight">{l.name}</div>
                <div className="text-xs opacity-80">{l.role}</div>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="rounded-full p-1.5 hover:bg-white/20 transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Messages */}
            <ScrollArea className="flex-1 px-4 py-3">
              <div className="space-y-3">
                {messages.map((msg, i) => (
                  <div
                    key={i}
                    className={cn("flex", msg.role === "user" ? "justify-end" : "justify-start")}
                  >
                    <div
                      className="max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed"
                      style={{
                        background:
                          msg.role === "user"
                            ? "linear-gradient(135deg, #3b82f6, #7c3aed)"
                            : theme === "dark"
                            ? "rgba(255,255,255,0.08)"
                            : "rgba(0,0,0,0.05)",
                        color: msg.role === "user" ? "#fff" : theme === "dark" ? "#f8fafc" : "#0f172a",
                        borderBottomLeftRadius: msg.role === "assistant" && !isRTL ? 4 : undefined,
                        borderBottomRightRadius:
                          (msg.role === "user" && !isRTL) || (msg.role === "assistant" && isRTL) ? 4 : undefined,
                      }}
                    >
                      {msg.content}
                    </div>
                  </div>
                ))}

                {loading && (
                  <div className="flex justify-start">
                    <div
                      className="rounded-2xl px-4 py-2.5"
                      style={{ background: theme === "dark" ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.05)" }}
                    >
                      <Loader2 size={18} className="animate-spin" style={{ color: "#7c3aed" }} />
                    </div>
                  </div>
                )}

                <div ref={bottomRef} />

                {offline && (
                  <div className="text-center py-2">
                    <p className="text-xs mb-2" style={{ color: theme === "dark" ? "#94a3b8" : "#64748b" }}>
                      {l.offline}
                    </p>
                    <a
                      href="/BookMeeting"
                      className="inline-block text-xs font-bold px-4 py-2 rounded-full"
                      style={{
                        background: "linear-gradient(135deg, #3b82f6, #7c3aed)",
                        color: "#fff",
                        textDecoration: "none",
                      }}
                    >
                      {l.offlineCta}
                    </a>
                  </div>
                )}
              </div>
            </ScrollArea>

            {/* Quick replies */}
            {messages.length <= 1 && !offline && (
              <div className="flex gap-2 px-4 pb-2 flex-wrap">
                {l.quickReplies.map((qr) => (
                  <button
                    key={qr.label}
                    onClick={() => sendMessage(qr.value)}
                    className="text-xs font-semibold px-3 py-1.5 rounded-full transition-colors"
                    style={{
                      background: theme === "dark" ? "rgba(124,58,237,0.15)" : "rgba(124,58,237,0.1)",
                      color: "#7c3aed",
                      border: "1px solid rgba(124,58,237,0.3)",
                    }}
                  >
                    {qr.label}
                  </button>
                ))}
              </div>
            )}

            {/* Input */}
            <form
              onSubmit={handleSubmit}
              className="flex items-center gap-2 px-3 py-3"
              style={{ borderTop: `1px solid ${theme === "dark" ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.08)"}` }}
            >
              <input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={l.placeholder}
                disabled={loading}
                className="flex-1 bg-transparent text-sm outline-none px-2"
                style={{
                  color: theme === "dark" ? "#f8fafc" : "#0f172a",
                  direction: isRTL ? "rtl" : "ltr",
                }}
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="rounded-full p-2 transition-colors disabled:opacity-40"
                style={{
                  background: input.trim() ? "linear-gradient(135deg, #3b82f6, #7c3aed)" : "transparent",
                  color: input.trim() ? "#fff" : theme === "dark" ? "#64748b" : "#94a3b8",
                }}
              >
                <Send size={16} className={isRTL ? "rotate-180" : ""} />
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

function getSessionId() {
  const key = "ziyada_chat_session";
  let id = sessionStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem(key, id);
  }
  return id;
}
