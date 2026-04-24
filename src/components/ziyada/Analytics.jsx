import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import posthog from "posthog-js";
import { trackPageView } from "@/lib/analytics";

export { trackEvent, identifyUser, trackPageView } from "@/lib/analytics";

const GA4_ID = import.meta.env.VITE_GA4_ID || "";
const PIXEL_ID = import.meta.env.VITE_META_PIXEL_ID || "";
const POSTHOG_KEY = import.meta.env.VITE_POSTHOG_KEY || "";
const HOTJAR_ID = import.meta.env.VITE_HOTJAR_ID || "";

function injectScript(id, src, onload) {
  if (document.getElementById(id)) return;
  const s = document.createElement("script");
  s.id = id; s.src = src; s.async = true;
  if (onload) s.onload = onload;
  document.head.appendChild(s);
}

function injectInlineScript(id, code) {
  if (document.getElementById(id)) return;
  const s = document.createElement("script");
  s.id = id; s.innerHTML = code;
  document.head.appendChild(s);
}

export default function Analytics() {
  const location = useLocation();

  // Initialize all tracking scripts once on mount
  useEffect(() => {
    /* ── Google Analytics 4 ── */
    if (GA4_ID && !GA4_ID.includes("X")) {
      injectScript("ga4-script", `https://www.googletagmanager.com/gtag/js?id=${GA4_ID}`, () => {
        injectInlineScript("ga4-config", `
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${GA4_ID}');
        `);
      });
    }

    /* ── Meta Pixel ── */
    if (PIXEL_ID && !PIXEL_ID.includes("X")) {
      injectInlineScript("meta-pixel", `
        !function(f,b,e,v,n,t,s)
        {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
        n.callMethod.apply(n,arguments):n.queue.push(arguments)};
        if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
        n.queue=[];t=b.createElement(e);t.async=!0;
        t.src=v;s=b.getElementsByTagName(e)[0];
        s.parentNode.insertBefore(t,s)}(window, document,'script',
        'https://connect.facebook.net/en_US/fbevents.js');
        fbq('init', '${PIXEL_ID}');
        fbq('track', 'PageView');
      `);
    }

    /* ── PostHog ── */
    const IS_LOCAL = window?.location?.hostname === 'localhost' || window?.location?.hostname === '127.0.0.1';
    if (POSTHOG_KEY && IS_LOCAL) {
      posthog.init(POSTHOG_KEY, {
        api_host: "https://us.i.posthog.com",
        autocapture: true,
        capture_pageview: true,
        capture_pageleave: true,
      });
    }

    /* ── Hotjar / Contentsquare ── */
    if (HOTJAR_ID && !HOTJAR_ID.includes("X")) {
      injectScript("hotjar-cs", `https://t.contentsquare.net/uxa/${HOTJAR_ID}.js`);
    }
  }, []);

  // Track page views on route changes
  useEffect(() => {
    trackPageView(location.pathname);
  }, [location.pathname]);

  return null;
}
