const STORAGE_PREFIX = 'ziyada_rl_'
const MAX_SUBMISSIONS = 3
const WINDOW_MS = 5 * 60 * 1000 // 5 minutes

export function checkRateLimit(formType) {
  try {
    const key = STORAGE_PREFIX + formType
    const now = Date.now()
    const stored = sessionStorage.getItem(key)
    let timestamps = stored ? JSON.parse(stored) : []

    // Remove expired timestamps
    timestamps = timestamps.filter(t => now - t < WINDOW_MS)

    if (timestamps.length >= MAX_SUBMISSIONS) {
      return { allowed: false, retryAfterMs: WINDOW_MS - (now - timestamps[0]) }
    }

    timestamps.push(now)
    sessionStorage.setItem(key, JSON.stringify(timestamps))
    return { allowed: true }
  } catch (e) {
    return { allowed: true } // fail open if sessionStorage unavailable
  }
}
