import { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import Footer from './Footer';
import ThreeBackground from './ThreeBackground.jsx';
import Analytics from './Analytics';
import FloatingChatWidget from '../ui/floating-chat-widget';
import FloatingVoiceWidget from '../ui/floating-voice-widget';
import { useTranslation } from './useTranslation';
import { captureUTMParams } from '@/lib/utm';

export default function ZiyadaLayout() {
  const { lang, t, isRTL, toggleLang } = useTranslation();
  const [theme, setTheme] = useState('dark');
  const location = useLocation();
  const isReadingRoute = location.pathname.startsWith('/Services');

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);

  useEffect(() => {
    document.documentElement.dir  = isRTL ? 'rtl' : 'ltr';
    document.documentElement.lang = lang;
  }, [lang, isRTL]);

  useEffect(() => {
    // Keep body background in sync so there's no flash of white behind the layout
    document.body.style.backgroundColor = theme === 'light' ? '#f8fafc' : '#0f172a';
    document.body.style.transition = 'background-color 0.5s ease';
  }, [theme]);

  useEffect(() => {
    captureUTMParams()
  }, [])

  const toggleTheme = () => setTheme(prev => prev === 'dark' ? 'light' : 'dark');

  const lightVars = theme === 'light' ? {
    '--bg-deep': '#f8fafc',
    '--bg-glass': 'rgba(255,255,255,0.82)',
    '--bg-card': 'rgba(255,255,255,0.9)',
    '--text-primary': '#000000',
    '--text-secondary': '#000000',
    '--text-muted': '#334155',
    '--accent-primary': '#2563eb',
    '--accent-glow': '#3b82f6',
    '--border-glass': 'rgba(15,23,42,0.08)',
    '--shadow-glass': '0 10px 40px rgba(15,23,42,0.12)',
    '--reading-overlay': 'transparent',
  } : {
    '--bg-deep': '#0f172a',
    '--bg-glass': 'rgba(15,23,42,0.6)',
    '--bg-card': 'rgba(30,41,59,0.4)',
    '--text-primary': '#ffffff',
    '--text-secondary': '#ffffff',
    '--accent-primary': '#3b82f6',
    '--accent-glow': '#8b5cf6',
    '--border-glass': 'rgba(255,255,255,0.1)',
    '--shadow-glass': '0 8px 32px 0 rgba(0,0,0,0.37)',
    '--reading-overlay': 'transparent',
  };

  return (
    <div className={theme === 'light' ? 'light-mode' : ''} style={{
      minHeight: '100vh',
      width: '100%',
      fontFamily: 'var(--font-body-ar, "Noto Kufi Arabic", sans-serif)',
      direction: isRTL ? 'rtl' : 'ltr',
      display: 'flex',
      flexDirection: 'column',
      overflowX: 'clip',
      backgroundColor: theme === 'light' ? '#f8fafc' : '#0f172a',
      color: theme === 'light' ? '#0f172a' : '#f8fafc',
      position: 'relative',
      zIndex: 1,
      transition: 'background-color 0.5s ease, color 0.5s ease',
      ...lightVars,
    }}>
      <Analytics />
      <ThreeBackground theme={theme} muted={isReadingRoute} />
      <div className="content-readability-layer" aria-hidden="true" />
      <Navbar t={t} lang={lang} toggleLang={toggleLang} isRTL={isRTL} theme={theme} toggleTheme={toggleTheme} />
      <main style={{ paddingTop: 'var(--header-height)', flex: 1, overflowX: 'clip' }}>
        <Outlet context={{ t, lang, isRTL, theme }} />
      </main>
      <Footer t={t} isRTL={isRTL} lang={lang} />
      <FloatingChatWidget lang={lang} theme={theme} />
      <FloatingVoiceWidget lang={lang} theme={theme} />
    </div>
  );
}
