import React, { useRef } from 'react';
import Vapi from '@vapi-ai/web';
// Use the actual widget icon used on your site
import VoiceWidgetIcon from '/assets/corporate-design-kit/icons/icon-chat.svg';

const VAPI_API_KEY = import.meta.env.VITE_VAPI_PUBLIC_KEY;
const VAPI_ASSISTANT_ID = import.meta.env.VITE_VAPI_ASSISTANT_ID;

const VoiceCallTrigger = () => {
  const vapiRef = useRef(null);

  const handleIconClick = () => {
    if (!VAPI_API_KEY || !VAPI_ASSISTANT_ID) {
      alert('Voice assistant is not configured. Please set VITE_VAPI_PUBLIC_KEY and VITE_VAPI_ASSISTANT_ID in your environment variables.');
      return;
    }
    if (!vapiRef.current) {
      vapiRef.current = new Vapi(VAPI_API_KEY);
    }
    vapiRef.current.start(VAPI_ASSISTANT_ID);
  };

  return (
    <span onClick={handleIconClick} style={{ cursor: 'pointer', display: 'inline-block', position: 'fixed', bottom: 24, right: 24, zIndex: 1000 }}>
      <img src={VoiceWidgetIcon} alt="Voice Assistant" style={{ width: 56, height: 56, boxShadow: '0 4px 16px rgba(59,130,246,0.18)', borderRadius: '50%' }} />
    </span>
  );
};

export default VoiceCallTrigger;
