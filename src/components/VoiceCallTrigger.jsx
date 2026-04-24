import React, { useRef } from 'react';
import Vapi from '@vapi-ai/web';

const VAPI_API_KEY = import.meta.env.VITE_VAPI_PUBLIC_KEY;
const VAPI_ASSISTANT_ID = import.meta.env.VITE_VAPI_ASSISTANT_ID;

const VoiceCallTrigger = () => {
  const vapiRef = useRef(null);

  const handleIconClick = () => {
    if (!VAPI_API_KEY || !VAPI_ASSISTANT_ID) {
      console.warn('Voice assistant: VITE_VAPI_PUBLIC_KEY or VITE_VAPI_ASSISTANT_ID not set.');
      return;
    }
    if (!vapiRef.current) {
      vapiRef.current = new Vapi(VAPI_API_KEY);
    }
    vapiRef.current.start(VAPI_ASSISTANT_ID);
  };

  return (
    <button
      onClick={handleIconClick}
      aria-label="Start voice assistant"
      style={{
        cursor: 'pointer',
        position: 'fixed',
        bottom: 88,
        right: 24,
        zIndex: 1000,
        width: 52,
        height: 52,
        borderRadius: '50%',
        border: 'none',
        background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
        boxShadow: '0 4px 16px rgba(59,130,246,0.35)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#fff',
        fontSize: 22,
      }}
    >
      🎙️
    </button>
  );
};

export default VoiceCallTrigger;
