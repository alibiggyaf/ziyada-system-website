import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Loader2, Mic, MicOff, PhoneCall, PhoneOff, X } from "lucide-react";
import { cn } from "@/lib/utils";
import Vapi from "@vapi-ai/web";

const T = {
  ar: {
    cta: "تحدث صوتياً",
    title: "المساعد الصوتي",
    subtitle: "شراكة ذكية لنمو عملك بخطوات واضحة وسريعة.",
    callStart: "ابدأ المكالمة",
    callEnd: "إنهاء المكالمة",
    connecting: "جاري الاتصال...",
    callActive: "المكالمة نشطة",
    userSpeaking: "أنت تتحدث...",
    assistantSpeaking: "زياد يتحدث...",
    emptyState: "اضغط «ابدأ المكالمة» للتحدث مع زياد مباشرة.",
    callEnded: "انتهت المكالمة.",
    error: "تعذّر الاتصال. تأكد من السماح بالمكروفون وحاول مرة أخرى.",
    noKey: "مفتاح VAPI مفقود — تحقق من VITE_VAPI_PUBLIC_KEY.",
    closeHint: "إغلاق المساعد الصوتي.",
  },
  en: {
    cta: "Talk Live",
    title: "Voice Assistant",
    subtitle: "Smart partnership for fast business growth.",
    callStart: "Start Call",
    callEnd: "End Call",
    connecting: "Connecting...",
    callActive: "Call active",
    userSpeaking: "You are speaking...",
    assistantSpeaking: "Ziyad is speaking...",
    emptyState: "Press «Start Call» to speak live with Ziyad.",
    callEnded: "Call ended.",
    error: "Could not connect. Allow microphone access and try again.",
    noKey: "VAPI key missing — check VITE_VAPI_PUBLIC_KEY.",
    closeHint: "Close voice assistant.",
  },
};

// Call state machine
const STATE = {
  IDLE: "idle",
  CONNECTING: "connecting",
  ACTIVE: "active",
  ENDED: "ended",
  ERROR: "error",
};

export default function FloatingVoiceWidget({ lang = "ar", theme = "dark" }) {
  const [open, setOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [callState, setCallState] = useState(STATE.IDLE);
  const [isMuted, setIsMuted] = useState(false);
  const [userSpeaking, setUserSpeaking] = useState(false);
  const [assistantSpeaking, setAssistantSpeaking] = useState(false);
  const [messages, setMessages] = useState([]); // [{role, text}]
  const [error, setError] = useState("");
  const [shouldWave, setShouldWave] = useState(false);
  const [interacted, setInteracted] = useState(false);
  const vapiRef = useRef(null);
  const messagesEndRef = useRef(null);

  const isRTL = lang === "ar";
  const copy = T[lang] || T.ar;

  const vapiPublicKey = import.meta.env.VITE_VAPI_PUBLIC_KEY || "";
  const vapiAssistantId = import.meta.env.VITE_VAPI_ASSISTANT_ID || "";
  const isActive = callState === STATE.ACTIVE;
  const isConnecting = callState === STATE.CONNECTING;

  // Scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Wave animation after 10–15 s
  useEffect(() => {
    if (interacted) return;
    const id = window.setTimeout(() => setShouldWave(true), 10000 + Math.floor(Math.random() * 5000));
    return () => window.clearTimeout(id);
  }, [interacted]);

  // Close voice panel when chat opens
  useEffect(() => {
    const onChatVis = (e) => {
      setChatOpen(!!e?.detail?.open);
      if (e?.detail?.open) closePanel();
    };
    const onVoiceOpenFromChat = () => {
      setChatOpen(true);
      openPanel();
    };
    window.addEventListener("ziyada-chat-visibility", onChatVis);
    window.addEventListener("ziyada-voice-open-from-chat", onVoiceOpenFromChat);
    return () => {
      window.removeEventListener("ziyada-chat-visibility", onChatVis);
      window.removeEventListener("ziyada-voice-open-from-chat", onVoiceOpenFromChat);
    };
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      vapiRef.current?.stop();
    };
  }, []);

  // ---- VAPI helpers ----
  function getOrCreateVapi() {
    if (vapiRef.current) return vapiRef.current;
    const vapi = new Vapi(vapiPublicKey);

    vapi.on("call-start", () => {
      setCallState(STATE.ACTIVE);
      setError("");
    });

    vapi.on("call-end", () => {
      setCallState(STATE.ENDED);
      setUserSpeaking(false);
      setAssistantSpeaking(false);
    });

    vapi.on("speech-start", () => setUserSpeaking(true));
    vapi.on("speech-end", () => setUserSpeaking(false));

    vapi.on("message", (msg) => {
      if (msg.type === "speech-update") {
        setAssistantSpeaking(msg.status === "started");
      }
      if (msg.type === "transcript" && msg.transcriptType === "final") {
        setMessages((prev) => {
          // If last entry has same role and is recent, replace; else append
          const last = prev[prev.length - 1];
          if (last?.role === msg.role && last?.partial) {
            return [...prev.slice(0, -1), { role: msg.role, text: msg.transcript }];
          }
          return [...prev, { role: msg.role, text: msg.transcript }];
        });
      }
      if (msg.type === "transcript" && msg.transcriptType === "partial") {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === msg.role && last?.partial) {
            return [...prev.slice(0, -1), { role: msg.role, text: msg.transcript, partial: true }];
          }
          return [...prev, { role: msg.role, text: msg.transcript, partial: true }];
        });
      }
    });

    vapi.on("error", (err) => {
      console.error("VAPI error:", err);
      setError(copy.error);
      setCallState(STATE.ERROR);
      setUserSpeaking(false);
      setAssistantSpeaking(false);
    });

    vapiRef.current = vapi;
    return vapi;
  }

  async function startCall() {
    if (!vapiPublicKey) { setError(copy.noKey); return; }
    setError("");
    setMessages([]);
    setCallState(STATE.CONNECTING);
    setInteracted(true);
    setShouldWave(false);
    try {
      const vapi = getOrCreateVapi();
      await vapi.start(vapiAssistantId);
    } catch (err) {
      let msg = copy.error;
      if (err && err.message && err.message.toLowerCase().includes("microphone")) {
        msg = lang === "ar"
          ? "تعذّر الوصول للميكروفون. يرجى السماح بالوصول للمكروفون من إعدادات المتصفح ثم إعادة المحاولة."
          : "Microphone access denied. Please allow mic permissions in your browser and try again.";
      }
      console.error("VAPI start failed:", err);
      setError(msg);
      setCallState(STATE.ERROR);
    }
  }

  function stopCall() {
    vapiRef.current?.stop();
    setCallState(STATE.IDLE);
    setUserSpeaking(false);
    setAssistantSpeaking(false);
    vapiRef.current = null;
  }

  function toggleMute() {
    const vapi = vapiRef.current;
    if (!vapi) return;
    const next = !isMuted;
    vapi.setMuted(next);
    setIsMuted(next);
  }

  const openPanel = () => { setShouldWave(false); setInteracted(true); setOpen(true); };
  const closePanel = () => { stopCall(); setOpen(false); };

  // ---- Status label ----
  let statusLabel = copy.emptyState;
  if (callState === STATE.CONNECTING) statusLabel = copy.connecting;
  if (callState === STATE.ACTIVE) {
    if (userSpeaking) statusLabel = copy.userSpeaking;
    else if (assistantSpeaking) statusLabel = copy.assistantSpeaking;
    else statusLabel = copy.callActive;
  }
  if (callState === STATE.ENDED) statusLabel = copy.callEnded;
  if (callState === STATE.ERROR) statusLabel = error || copy.error;

  return (
    <>
      {/* Floating button (hidden when chatOpen) */}
      <AnimatePresence>
        {!open && !chatOpen && (
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="fixed z-50 flex items-center gap-2"
            style={{ bottom: "calc(env(safe-area-inset-bottom,0px) + 84px)", right: 24, direction: "ltr" }}
          >
            <motion.button
              onClick={openPanel}
              className="relative flex h-12 w-12 items-center justify-center rounded-full text-white transition-transform hover:scale-105"
              style={{
                background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
                boxShadow: "0 8px 26px rgba(59,130,246,0.35)",
                animation: shouldWave ? "voiceWave 1.8s ease-in-out infinite" : "none",
              }}
              aria-label={copy.title}
            >
              <Mic size={20} />
              {shouldWave && <span className="voice-wave-ring" />}
            </motion.button>
            <div
              className="rounded-full px-3 py-1 text-xs font-semibold voice-widget-label"
              style={{
                background: theme === "dark" ? "rgba(15,23,42,0.88)" : "rgba(255,255,255,0.95)",
                color: "#3b82f6",
                border: "1px solid rgba(59,130,246,0.28)",
                backdropFilter: "blur(10px)",
              }}
            >
              {copy.cta}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Mic icon for chat widget header is now rendered inside the chat widget header for correct positioning */}

      {/* Voice panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 16, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 16, scale: 0.96 }}
            transition={{ duration: 0.2 }}
            dir={isRTL ? "rtl" : "ltr"}
            className="fixed z-50 w-[360px] max-w-[calc(100vw-32px)] overflow-hidden rounded-2xl shadow-2xl"
            style={{
              zIndex: 9999,
              bottom: "calc(env(safe-area-inset-bottom,0px) + 84px)",
              right: 24,
              border: `1px solid ${theme === "dark" ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)"}`,
              background: theme === "dark" ? "#0f172a" : "#ffffff",
            }}
          >
            {/* Header */}
            <div
              className="flex items-center gap-2 px-4 py-3 text-white"
              style={{ background: "linear-gradient(135deg, #1e3a8a, #8b5cf6)" }}
            >
              <PhoneCall size={18} className={cn(isActive && "animate-pulse")} />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-bold">{copy.title}</p>
                <p className="truncate text-xs opacity-85">{copy.subtitle}</p>
              </div>
              <button
                onClick={closePanel}
                className="rounded-full p-1.5 hover:bg-white/20"
                aria-label={copy.closeHint}
              >
                <X size={16} />
              </button>
            </div>

            {/* Conversation area */}
            <div
              className="space-y-2 overflow-y-auto px-4 py-3"
              style={{ minHeight: 90, maxHeight: 220 }}
            >
              {messages.length === 0 && (
                <p
                  className="text-sm"
                  style={{ color: theme === "dark" ? "#94a3b8" : "#475569" }}
                >
                  {statusLabel}
                </p>
              )}
              {messages.map((m, i) => (
                <div
                  key={i}
                  className={cn("flex", m.role === "user" ? (isRTL ? "justify-end" : "justify-start") : (isRTL ? "justify-start" : "justify-end"))}
                >
                  <div
                    className={cn("rounded-xl px-3 py-1.5 text-sm max-w-[85%]", m.partial && "opacity-60")}
                    style={
                      m.role === "assistant"
                        ? { background: "linear-gradient(135deg,#1e3a8a,#8b5cf6)", color: "#fff" }
                        : {
                            background: theme === "dark" ? "rgba(255,255,255,0.08)" : "rgba(15,23,42,0.07)",
                            color: theme === "dark" ? "#e2e8f0" : "#0f172a",
                          }
                    }
                  >
                    {m.text}
                  </div>
                </div>
              ))}
              {/* Live speaking indicator */}
              {isActive && (assistantSpeaking || userSpeaking) && messages.length > 0 && (
                <p className="text-xs" style={{ color: "#8b5cf6" }}>{statusLabel}</p>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Controls */}
            <div className="flex gap-2 px-4 pb-4">
              {!isActive && !isConnecting ? (
                <button
                  onClick={startCall}
                  disabled={isConnecting}
                  className="flex flex-1 items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold text-white disabled:opacity-60"
                  style={{ background: "linear-gradient(135deg, #3b82f6, #8b5cf6)" }}
                >
                  <PhoneCall size={16} />
                  {copy.callStart}
                </button>
              ) : isConnecting ? (
                <button
                  disabled
                  className="flex flex-1 items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold text-white opacity-70"
                  style={{ background: "linear-gradient(135deg,#3b82f6,#8b5cf6)" }}
                >
                  <Loader2 size={16} className="animate-spin" />
                  {copy.connecting}
                </button>
              ) : (
                <>
                  <button
                    onClick={toggleMute}
                    className="flex items-center justify-center rounded-xl p-3"
                    style={{
                      background: isMuted
                        ? "rgba(239,68,68,0.15)"
                        : theme === "dark" ? "rgba(255,255,255,0.07)" : "rgba(15,23,42,0.06)",
                      color: isMuted ? "#ef4444" : theme === "dark" ? "#94a3b8" : "#475569",
                    }}
                    aria-label={isMuted ? "Unmute" : "Mute"}
                  >
                    {isMuted ? <MicOff size={18} /> : <Mic size={18} />}
                  </button>
                  <button
                    onClick={stopCall}
                    className="flex flex-1 items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold text-white"
                    style={{ background: "linear-gradient(135deg,#ef4444,#f97316)" }}
                  >
                    <PhoneOff size={16} />
                    {copy.callEnd}
                  </button>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`
        @keyframes voiceWave {
          0%, 100% { transform: translateY(0) rotate(0deg); }
          25% { transform: translateY(-2px) rotate(-3deg); }
          75% { transform: translateY(-2px) rotate(3deg); }
        }
        .voice-wave-ring {
          position: absolute;
          inset: -4px;
          border-radius: 9999px;
          border: 2px solid rgba(59,130,246,0.45);
          animation: waveRing 1.8s ease-out infinite;
          pointer-events: none;
        }
        @keyframes waveRing {
          0% { transform: scale(0.9); opacity: 0.8; }
          100% { transform: scale(1.3); opacity: 0; }
        }
        @media (max-width: 768px) {
          .voice-widget-label { display: none !important; }
        }
      `}</style>
    </>
  );
}
