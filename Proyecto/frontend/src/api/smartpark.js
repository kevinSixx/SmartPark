import {
  clearSession,
  getAccessToken,
} from "../utils/session.js"


export const API_URL = (
  import.meta.env?.VITE_API_URL || ""
).replace(/\/$/, "")


async function parseError(response) {
  try {
    return (await response.json())?.detail
  } catch {
    return null
  }
}

function apiError(response, detail, operation = "general") {
  const status = response.status
  const raw = typeof detail === "string" ? detail : JSON.stringify(detail ?? "")
  let message

  if (status === 401) message = "Tu sesión ha expirado. Inicia sesión nuevamente."
  else if (status === 403) message = "No tienes permisos para realizar esta acción."
  else if (status === 404) message = "No se encontró el recurso solicitado."
  else if (status === 422 || status === 400) message = "Revisa los datos ingresados e inténtalo nuevamente."
  else if (status >= 500) message = "SmartPark no está disponible temporalmente. Inténtalo nuevamente."
  else message = "Ocurrió un problema. Inténtalo nuevamente."

  if (operation === "enroll" && (status === 400 || status === 422)) {
    message = /face|rostro|detect/i.test(raw)
      ? "No se detectó un rostro válido en alguna fotografía. Usa imágenes claras con una sola persona."
      : "No se pudo registrar el rostro. Revisa las fotografías e inténtalo nuevamente."
  }

  const error = new Error(message)
  error.status = status
  return error
}

function networkError() {
  const error = new Error("No se pudo conectar con SmartPark. Inténtalo nuevamente.")
  error.status = 0
  return error
}

async function fetchSmartpark(path, options) {
  try {
    return await fetch(`${API_URL}${path}`, options)
  } catch {
    throw networkError()
  }
}


async function request(
  path,
  options = {},
  {
    auth = false,
  } = {}
) {

  const headers = new Headers(
    options.headers || {}
  )

  if (auth) {

    const token = getAccessToken()

    if (token) {

      headers.set(
        "Authorization",
        `Bearer ${token}`
      )
    }
  }


  const response = await fetchSmartpark(
    path,
    {
      ...options,
      headers,
    }
  )


  if (
    response.status === 401
    &&
    auth
  ) {

    clearSession()
  }


  if (!response.ok) {

    throw apiError(response, await parseError(response))
  }


  if (response.status === 204) {
    return null
  }


  return response.json()
}


/* ============================================================
   SISTEMA
   ============================================================ */

export function getBackendHealth() {

  return request(
    "/health"
  )
}


/* ============================================================
   AUTENTICACION
   ============================================================ */

export function loginStaff(
  username,
  password
) {

  return request(
    "/api/v1/auth/login",
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({
        username,
        password,
      }),
    }
  )
}


export function getCurrentStaff() {

  return request(
    "/api/v1/auth/me",
    {},
    {
      auth: true,
    }
  )
}


/* ============================================================
   PERSONAL / ADMINISTRADORES / GUARDIAS
   ============================================================ */

export function getStaffAccounts() {

  return request(
    "/api/v1/staff",
    {},
    {
      auth: true,
    }
  )
}


export function getStaffAccount(
  staffId
) {

  return request(
    `/api/v1/staff/${staffId}`,
    {},
    {
      auth: true,
    }
  )
}


export function createStaffAccount(
  data
) {

  return request(
    "/api/v1/staff",
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify(
        data
      ),
    },
    {
      auth: true,
    }
  )
}


export function updateStaffAccount(
  staffId,
  data
) {

  return request(
    `/api/v1/staff/${staffId}`,
    {
      method: "PATCH",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify(
        data
      ),
    },
    {
      auth: true,
    }
  )
}


/* ============================================================
   USUARIOS DEL PARQUEADERO
   ============================================================ */

export function getUsers() {

  return request(
    "/api/v1/users"
  )
}


export function getUser(
  userId
) {

  return request(
    `/api/v1/users/${userId}`
  )
}


export function createUser(
  data
) {

  return request(
    "/api/v1/users",
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify(
        data
      ),
    }
  )
}


/* ============================================================
   VEHICULOS
   ============================================================ */

export function getVehicles() {

  return request(
    "/api/v1/vehicles"
  )
}


export function createVehicle(
  data
) {

  return request(
    "/api/v1/vehicles",
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify(
        data
      ),
    }
  )
}


/* ============================================================
   PERMISOS
   ============================================================ */

export function getPermissions() {

  return request(
    "/api/v1/permissions"
  )
}


export function createPermission(
  data
) {

  return request(
    "/api/v1/permissions",
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify(
        data
      ),
    }
  )
}


/* ============================================================
   HISTORIAL DE ACCESOS
   ============================================================ */

export function getAccessEvents() {

  return request(
    "/api/v1/access-events"
  )
}


/* ============================================================
   PROCESAMIENTO DE ACCESO
   ============================================================ */

export async function processAccess(
  faceImage,
  plateImage,
  eventType
) {

  const formData = new FormData()

  formData.append(
    "face_image",
    faceImage
  )

  formData.append(
    "plate_image",
    plateImage
  )

  formData.append(
    "event_type",
    eventType
  )


  const response = await fetchSmartpark(
    "/api/v1/access/process",
    {
      method: "POST",
      body: formData,
    }
  )


  if (!response.ok) {

    throw apiError(response, await parseError(response))
  }

  return response.status === 204 ? null : response.json()
}


/* ============================================================
   CONTROL MANUAL DE BARRERA
   ============================================================ */

export function openGateManually(
  gateId,
  {
    reason,
    observation = null,
    accessEventId = null,
  }
) {

  return request(
    `/api/v1/gates/${gateId}/open`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({

        reason,

        observation,

        access_event_id:
          accessEventId,
      }),
    },
    {
      auth: true,
    }
  )
}


export function closeGateManually(
  gateId,
  {
    observation = null,
    accessEventId = null,
  } = {}
) {

  return request(
    `/api/v1/gates/${gateId}/close`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({

        observation,

        access_event_id:
          accessEventId,
      }),
    },
    {
      auth: true,
    }
  )
}


export function getGateActions(
  gateId = "gate-01",
  limit = 20
) {

  return request(
    `/api/v1/gates/${gateId}/actions?limit=${limit}`,
    {},
    {
      auth: true,
    }
  )
}


/* ============================================================
   PERFIL FACIAL
   ============================================================ */

export function getFaceProfile(
  userId
) {

  return request(
    `/api/v1/face-profiles/${userId}`
  )
}


export async function enrollFace(
  userId,
  images
) {

  const formData = new FormData()

  formData.append("user_id", String(userId))


  images.forEach(
    (image) => {

      formData.append(
        "images",
        image
      )
    }
  )


  const response = await fetchSmartpark(
    "/api/v1/face-profiles/enroll",
    {
      method: "POST",
      body: formData,
    }
  )


  if (!response.ok) {

    throw apiError(response, await parseError(response), "enroll")
  }

  return response.status === 204 ? null : response.json()
}
