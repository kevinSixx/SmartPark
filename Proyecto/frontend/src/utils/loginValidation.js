export function validateLogin(username, password) {
  if (!username.trim()) return "Ingresa tu usuario."
  if (!password) return "Ingresa tu contraseña."
  if (password.length < 6) return "La contraseña debe tener al menos 6 caracteres."
  return ""
}

export function loginErrorMessage(status) {
  if (status === 401 || status === 403) return "Usuario o contraseña incorrectos."
  if (status === 0 || status >= 500) return "No se pudo conectar con SmartPark. Inténtalo nuevamente."
  return "Ocurrió un problema al iniciar sesión. Inténtalo nuevamente."
}
