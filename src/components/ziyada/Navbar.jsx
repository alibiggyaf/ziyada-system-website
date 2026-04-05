import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Moon, Sun, Menu, X, Globe } from "lucide-react";
import { GlassButton } from "@/components/ui/glass-button";

const NAV = {
  ar: [
    { label: "الرئيسية", path: "/Home" },
    { label: "لماذا زيادة", path: "/Why" },
    { label: "خدماتنا", path: "/Services" },
    { label: "من نحن", path: "/About" },
    { label: "قصص النجاح", path: "/Cases" },
    { label: "المدونة", path: "/Blog" },
  ],
  en: [
    { label: "Home", path: "/Home" },
    { label: "Why Ziyada", path: "/Why" },
    { label: "Services", path: "/Services" },
    { label: "About", path: "/About" },
    { label: "Success Stories", path: "/Cases" },
    { label: "Blog", path: "/Blog" },
  ]
};

export default function Navbar({ lang, toggleLang, theme, toggleTheme, isRTL: _isRTL }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  const isRTL = lang === "ar";

  return (
    <header className="glass-topbar" dir={isRTL ? "rtl" : "ltr"}>
      <div className="glass-topbar-inner">
        {/* Logo */}
        <Link to="/Home" style={{ textDecoration: "none" }}>
          <span className="brand-wordmark" style={{ fontSize: "1.3rem", fontWeight: 900, letterSpacing: "-0.02em" }}>
            Ziyada Systems
          </span>
        </Link>

        {/* Desktop Nav */}
        <nav style={{ display: "flex", gap: 28, listStyle: "none" }} className="hidden-mobile">
          {NAV[lang].map(item => (
            <Link key={item.path} to={item.path} style={{
              textDecoration: "none", fontSize: "0.9rem", fontWeight: 500,
              color: location.pathname === item.path ? "var(--accent-primary)" : "var(--text-secondary)",
              transition: "color 0.2s"
            }}>
              {item.label}
            </Link>
          ))}
        </nav>

        {/* Controls */}
        <div className="glass-topbar-controls">
          <GlassButton size="icon" onClick={toggleTheme} aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}>
            {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
          </GlassButton>
          <GlassButton size="sm" onClick={toggleLang} contentClassName="flex items-center gap-1.5">
            <Globe size={14} /> {lang === "ar" ? "EN" : "AR"}
          </GlassButton>
          <Link to="/BookMeeting" className="nav-cta-link">
            <GlassButton size="sm" contentClassName="font-bold">
              {lang === "ar" ? "احجز استشارة" : "Book Consultation"}
            </GlassButton>
          </Link>
          <GlassButton
            size="icon"
            onClick={() => setMobileOpen(o => !o)}
            className="mobile-menu-btn"
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X size={22} /> : <Menu size={22} />}
          </GlassButton>
        </div>

      </div>

      {/* Mobile Nav */}
      {mobileOpen && (
        <div className="glass-mobile-nav"
          dir={isRTL ? "rtl" : "ltr"}>
          {NAV[lang].map(item => (
            <Link key={item.path} to={item.path}
              onClick={() => setMobileOpen(false)}
              style={{ display: "block", padding: "10px 0", textDecoration: "none", color: "var(--text-secondary)", fontWeight: 600, borderBottom: "1px solid var(--border-glass)" }}>
              {item.label}
            </Link>
          ))}
        </div>
      )}

      <style>{`
        .glass-topbar {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          z-index: 100;
          padding: 8px 18px 0;
          background: transparent;
        }

        .glass-topbar-inner {
          max-width: 1200px;
          margin: 0 auto;
          height: 64px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 16px;
          padding: 0 16px;
          border-radius: 999px;
          background: linear-gradient(135deg, rgba(86, 98, 138, 0.52), rgba(46, 58, 98, 0.44));
          border: 1px solid rgba(180, 196, 242, 0.36);
          box-shadow: 0 10px 26px rgba(2, 6, 23, 0.28);
          backdrop-filter: blur(14px) saturate(140%);
          -webkit-backdrop-filter: blur(14px) saturate(140%);
        }

        .glass-topbar-controls {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .glass-topbar-controls .glass-button {
          border-color: rgba(233, 241, 255, 0.34);
          background: linear-gradient(135deg, rgba(255,255,255,0.22), rgba(255,255,255,0.08));
          color: #f8fafc;
        }

        .brand-wordmark {
          background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 40%, #c4b5fd 100%);
          -webkit-background-clip: text;
          background-clip: text;
          -webkit-text-fill-color: transparent;
          color: transparent;
        }

        .light-mode .brand-wordmark {
          background: none;
          -webkit-text-fill-color: #0f172a;
          color: #0f172a;
          text-shadow: 0 1px 0 rgba(255, 255, 255, 0.5);
        }

        .glass-mobile-nav {
          max-width: 1200px;
          margin: 10px auto 0;
          padding: 14px 24px;
          border-radius: 20px;
          background: linear-gradient(135deg, rgba(255,255,255,0.24), rgba(255,255,255,0.08));
          border: 1px solid rgba(255,255,255,0.2);
          backdrop-filter: blur(14px) saturate(140%);
          -webkit-backdrop-filter: blur(14px) saturate(140%);
        }

        .topbar-mobile-cats {
          display: none;
        }

        @media (max-width: 768px) {
          .hidden-mobile { display: none !important; }
          .mobile-menu-btn { display: flex !important; }
          .nav-cta-link { display: none !important; }
          .glass-topbar { padding: 8px 10px 0; }
          .glass-topbar-inner {
            height: 60px;
            min-height: 60px;
            gap: 8px;
            flex-wrap: nowrap;
            padding-top: 0;
            padding-bottom: 0;
            border-radius: 999px;
          }
        }

        .btn-cta { white-space: nowrap; }
      `}</style>
    </header>
  );
}