/**
 * Ziyada Brand Icon Set
 * Custom SVG icons matching the dark-tech purple/cyan brand identity.
 */
import React from "react";

function I(props) {
  const { size, children, style } = props;
  const svgSize = typeof size === "number" ? size : 24;
  return (
    <svg width={svgSize} height={svgSize} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" style={style}>
      {children}
    </svg>
  );
}

export const IconZap = (props) => (
  <I {...props}><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" /></I>
);
export const IconTarget = (props) => (
  <I {...props}><circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" /></I>
);
export const IconRocket = (props) => (
  <I {...props}>
    <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z" />
    <path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z" />
    <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0" />
    <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5" />
  </I>
);
export const IconMegaphone = (props) => (
  <I {...props}><path d="m3 11 19-9-9 19-2-8-8-2z" /></I>
);
export const IconGlobe = (props) => (
  <I {...props}><circle cx="12" cy="12" r="10" /><ellipse cx="12" cy="12" rx="10" ry="4" /><ellipse cx="12" cy="12" rx="4" ry="10" /></I>
);
export const IconBarChart = (props) => (
  <I {...props}><line x1="12" y1="20" x2="12" y2="10" /><line x1="18" y1="20" x2="18" y2="4" /><line x1="6" y1="20" x2="6" y2="16" /></I>
);
export const IconShare = (props) => (
  <I {...props}>
    <circle cx="18" cy="5" r="3" /><circle cx="6" cy="12" r="3" /><circle cx="18" cy="19" r="3" />
    <line x1="8.59" y1="13.51" x2="15.42" y2="10.49" />
  </I>
);
export const IconCrosshair = (props) => (
  <I {...props}><circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="3" /></I>
);
export const IconHandshake = (props) => (
  <I {...props}>
    <path d="M20.42 4.58a5.4 5.4 0 0 0-7.65 0l-.77.78-.77-.78a5.4 5.4 0 0 0-7.65 0C1.46 6.7 1.33 10.28 4 13l8 8 8-8c2.67-2.72 2.54-6.3.42-8.42z" />
  </I>
);
export const IconTrendingUp = (props) => (
  <I {...props}><polyline points="22 7 13.5 15.5 8.5 10.5 2 17" /><polyline points="16 7 22 7 22 13" /></I>
);
export const IconRefresh = (props) => (
  <I {...props}>
    <polyline points="23 4 23 10 17 10" /><polyline points="1 20 1 14 7 14" />
    <path d="M3.51 9a9 9 0 1 1 2.13 9.36" />
  </I>
);
export const IconClockAlert = (props) => (
  <I {...props}>
    <circle cx="12" cy="12" r="10" />
    <polyline points="12 6 12 12 16 14" />
    <line x1="12" y1="16" x2="12" y2="18" />
    <line x1="12" y1="20" x2="12" y2="20" />
  </I>
);
export const IconTrendingDown = (props) => (
  <I {...props}><polyline points="22 17 13.5 8.5 8.5 13.5 2 7" /><polyline points="16 17 22 17 22 11" /></I>
);
export const IconEyeOff = (props) => (
  <I {...props}>
    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
  </I>
);
export const IconUnlink = (props) => (
  <I {...props}>
    <path d="M18.84 12.25l1.72-1.71h-.02a5.004 5.004 0 0 0-.12-7.07 5.006 5.006 0 0 0-6.95 0l-1.72 1.71" />
    <path d="M5.17 11.75l-1.71 1.71a5.004 5.004 0 0 0 .12 7.07 5.006 5.006 0 0 0 6.95 0l1.71-1.71" />
    <line x1="8" y1="2" x2="8" y2="5" />
    <line x1="2" y1="8" x2="5" y2="8" />
    <line x1="16" y1="19" x2="16" y2="22" />
    <line x1="19" y1="16" x2="22" y2="16" />
  </I>
);
export const IconCalculator = (props) => (
  <I {...props}>
    <rect x="4" y="2" width="16" height="20" rx="2" />
    <line x1="8" y1="6" x2="16" y2="6" />
    <line x1="8" y1="10" x2="10" y2="10" /><line x1="14" y1="10" x2="16" y2="10" />
    <line x1="8" y1="14" x2="10" y2="14" /><line x1="14" y1="14" x2="16" y2="14" />
    <line x1="8" y1="18" x2="16" y2="18" />
  </I>
);
export const IconCheck = (props) => (
  <I {...props}>
    <polyline points="20 6 9 17 4 12" />
  </I>
);
export const IconUser = (props) => (
  <I {...props}>
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </I>
);
export const IconMapPin = (props) => (
  <I {...props}>
    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
    <circle cx="12" cy="10" r="3" />
  </I>
);
export const IconClock = (props) => (
  <I {...props}>
    <circle cx="12" cy="12" r="10" />
    <polyline points="12 6 12 12 16 14" />
  </I>
);