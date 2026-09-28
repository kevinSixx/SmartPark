const SESSION_KEY = "smartpark_session"

export function getSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function setSession(session) {
  localStorage.setItem(
    SESSION_KEY,
    JSON.stringify(session)
  )
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY)
}

export function getAccessToken() {
  return getSession()?.accessToken || ""
}

export function getSessionRole() {
  return String(getSession()?.role || "").toUpperCase()
}
