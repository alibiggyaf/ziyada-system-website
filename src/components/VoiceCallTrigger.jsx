import { useRef } from 'react';
import Vapi from '@vapi-ai/web';

const VAPI_API_KEY = import.meta.env.VITE_VAPI_PUBLIC_KEY;
const VAPI_ASSISTANT_ID = import.meta.env.VITE_VAPI_ASSISTANT_ID;

export default function VoiceCallTrigger() {
  const vapiRef = useRef(null);

  const handleClick = () => {
    if (!VAPI_API_KEY || !VAPI_ASSISTANT_ID) {
      console.warn('VoiceCallTrigger: VITE_VAPI_PUBLIC_KEY or VITE_VAPI_ASSISTANT_ID not set.');
      return;
    }
    if (!vapiRef.current) {
      vapiRef.current = new Vapi(VAPI_API_KEY);
    }
    vapiRef.current.start(VAPI_ASSISTANT_ID);
  };

  return (
    <>
      <button
        onClick={handleClick}
        aria-label="Start voice assistant"
        style={{
          position: 'fixed',
          bottom: 88,
          right: 24,
          zIndex: 1000,
          width: 52,
          height: 52,
          borderRadius: '50%',
          border: 'none',
          background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
          boxShadow: '0 8px 26px rgba(59,130,246,0.35)',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'transform 0.2s ease, box-shadow 0.2s ease',
        }}
        onMouseEnter={e => {
          e.currentTarget.style.transform = 'scale(1.1)';
          e.currentTarget.style.boxShadow = '0 12px 32px rgba(59,130,246,0.5)';
        }}
        onMouseLeave={e => {
          e.currentTarget.style.transform = 'scale(1)';
          e.currentTarget.style.boxShadow = '0 8px 26px rgba(59,130,246,0.35)';
        }}
      >
        {/* Mic SVG inline — no external file needed */}
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
          <line x1="12" y1="19" x2="12" y2="23"/>
          <line x1="8" y1="23" x2="16" y2="23"/>
        </svg>
      </button>
      <style>{`
        @keyframes voicePulse {
          0%, 100% { box-shadow: 0 8px 26px rgba(59,130,246,0.35); }
          50% { box-shadow: 0 8px 36px rgba(139,92,246,0.55); }
        }
      `}</style>
    </>
  );
}
