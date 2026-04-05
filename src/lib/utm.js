const UTM_PARAMS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']
const STORAGE_KEY = 'ziyada_utm'

export function captureUTMParams() {
  try {
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
