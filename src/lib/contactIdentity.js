const KEY = "ziyada_contact_identity";
const SESSION_KEY = "ziyada_chat_session";

export function setKnownIdentity(identity) {
  try {
    const existing = getKnownIdentity() || {};
    localStorage.setItem(KEY, JSON.stringify({ ...existing, ...identity }));
  } catch {}
}

export function getKnownIdentity() {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function getChatSessionId() {
  try {
    let id = sessionStorage.getItem(SESSION_KEY);
    if (!id) {
      id = crypto.randomUUID();
      sessionStorage.setItem(SESSION_KEY, id);
    }
    return id;
  } catch {
    return "anon";
  }
}
