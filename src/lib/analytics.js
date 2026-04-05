export function trackEvent(eventName, properties = {}) {
  // GA4
  if (window.gtag) {
    window.gtag('event', eventName, properties);
  }
  // PostHog
  if (window.posthog) {
    window.posthog.capture(eventName, properties);
  }
  // Meta Pixel
  if (window.fbq) {
    window.fbq('trackCustom', eventName, properties);
  }
}

export function identifyUser(email, properties = {}) {
  if (window.posthog) {
    window.posthog.identify(email, properties);
  }
}

export function trackPageView(path) {
  if (window.gtag) {
    window.gtag('event', 'page_view', { page_path: path });
  }
  if (window.posthog) {
    window.posthog.capture('$pageview', { $current_url: path });
  }
}
