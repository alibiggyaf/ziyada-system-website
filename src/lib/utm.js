const UTM_PARAMS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']
const STORAGE_KEY = 'ziyada_utm'
const LANDING_PAGE_KEY = 'ziyada_landing_page_url'

export function captureUTMParams() {
  try {
    if (!sessionStorage.getItem(LANDING_PAGE_KEY)) {
      sessionStorage.setItem(LANDING_PAGE_KEY, window.location.href)
    }
    const params = new URLSearchParams(window.location.search)
    const utm = {}
    let hasUTM = false
    for (const key of UTM_PARAMS) {
      const val = params.get(key)
      if (val) {
        utm[key] = val
        hasUTM = true
      }
    }
    if (hasUTM) {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(utm))
    }
  } catch (e) {
    // sessionStorage not available
  }
}

export function getUTMParams() {
  try {
    const stored = sessionStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : {}
  } catch (e) {
    return {}
  }
}

export function getSourcePage() {
  return window.location.pathname
}

export function getPageUrl() {
  try {
    return window.location.href
  } catch (e) {
    return null
  }
}

export function getLandingPageUrl() {
  try {
    return sessionStorage.getItem(LANDING_PAGE_KEY) || window.location.href
  } catch (e) {
    return null
  }
}

export function getReferrerUrl() {
  try {
    return document.referrer || null
  } catch (e) {
    return null
  }
}
