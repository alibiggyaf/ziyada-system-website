import { useRef, useEffect, useState } from "react";
import { Link } from "react-router-dom";

/**
 * Service card with:
 * - scroll-triggered fade-in + slide-up
 * - animated rainbow/gradient border frame on hover (and idle pulse)
 * - light mode aware
 */
export default function AnimatedServiceCard({ svc, index, isRTL, Arrow, theme }) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);
  const [hovered, setHovered] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setVisible(true); obs.disconnect(); } },
      { threshold: 0.1 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  const delay = `${index * 80}ms`;
  const isLight = theme === "light";

  return (
    <div
      ref={ref}
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(36px)",
        transition: `opacity 0.55s ease ${delay}, transform 0.55s ease ${delay}`,
      }}
    >
      <Link to={svc.path || "/Services"} style={{ textDecoration: "none", display: "block", height: "100%" }}>
        {/* Animated border wrapper */}
        <div
          style={{
            position: "relative",
            borderRadius: 18,
            padding: 2,
            background: hovered
              ? "linear-gradient(135deg, #3b82f6, #8b5cf6, #06b6d4, #3b82f6)"
              : isLight
              ? "rgba(59,130,246,0.18)"
              : "rgba(59,130,246,0.12)",
            backgroundSize: "300% 300%",
            animation: hovered ? "cardBorderSpin 2.5s linear infinite" : "none",
            transition: "background 0.4s",
            boxShadow: hovered
              ? "0 0 24px rgba(139,92,246,0.45), 0 8px 32px rgba(59,130,246,0.25)"
              : "none",
          }}
          onMouseEnter={() => setHovered(true)}
          onMouseLeave={() => setHovered(false)}
        >
          <div
            style={{
              borderRadius: 16,
              padding: 28,
              background: isLight
                ? hovered ? "rgba(255,255,255,0.98)" : "rgba(255,255,255,0.88)"
                : hovered ? "rgba(15,23,42,0.97)" : "rgba(15,23,42,0.75)",
              backdropFilter: "blur(16px)",
              display: "flex",
              flexDirection: "column",
              height: "100%",
              transition: "background 0.3s",
            }}
          >
            {/* Icon */}
            <div style={{
              width: 46, height: 46, borderRadius: 12, marginBottom: 16,
              display: "flex", alignItems: "center", justifyContent: "center",
              background: hovered
                ? "linear-gradient(135deg, #3b82f6, #8b5cf6)"
                : isLight ? "rgba(59,130,246,0.12)" : "rgba(124,58,237,0.14)",
              color: hovered ? "#fff" : "var(--accent-primary)",
              transition: "background 0.35s, color 0.35s",
              boxShadow: hovered ? "0 4px 16px rgba(59,130,246,0.4)" : "none",
            }}>
              <svc.Icon size={22} />
            </div>

            {/* Title */}
            <h3 style={{
              fontWeight: 700, marginBottom: 10, fontSize: "1.05rem",
              color: isLight ? "#1e293b" : "#f8fafc",
              lineHeight: 1.4,
            }}>
              {svc.title}
            </h3>

            {/* Desc */}
            <p style={{
              fontSize: "0.88rem", lineHeight: 1.75, flex: 1,
              color: isLight ? "#475569" : "rgba(248,250,252,0.65)",
            }}>
              {svc.desc}
            </p>

            {/* CTA row */}
            {svc.path && (
              <div style={{
                marginTop: 18, display: "flex", alignItems: "center", gap: 6,
                color: "var(--accent-primary)", fontSize: "0.82rem", fontWeight: 700,
                opacity: hovered ? 1 : 0.75, transition: "opacity 0.3s",
              }}>
                {isRTL ? "اكتشف التفاصيل" : "Explore details"} <Arrow size={13} />
              </div>
            )}
          </div>
        </div>
      </Link>

      <style>{`
        @keyframes cardBorderSpin {
          0%   { background-position: 0% 50%; }
          50%  { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
      `}</style>
    </div>
  );
}