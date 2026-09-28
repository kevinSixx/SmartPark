import {
  clearSession,
  getAccessToken,
} from "../utils/session"


export const API_URL = (
  import.meta.env.VITE_API_URL || ""
).replace(/\/$/, "")


async function parseError(
  response,
  fallback
) {
  try {
    const body = await response.json()

    return (
      body?.detail
      ||
      fallback
    )

  } catch {

    return fallback
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


  const response = await fetch(
    `${API_URL}${path}`,
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

    const detail = await parseError(
      response,
      "Error al comunicarse con SmartPark"
    )

    throw new Error(
      typeof detail === "string"
        ? detail
        : JSON.stringify(detail)
    )
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


  const response = await fetch(
    `${API_URL}/api/v1/access/process`,
    {
      method: "POST",
      body: formData,
    }
  )


  if (!response.ok) {

    const detail = await parseError(
      response,
      "No se pudo procesar el acceso"
    )

    throw new Error(
      typeof detail === "string"
        ? detail
        : JSON.stringify(detail)
    )
  }


  return response.json()
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
   ESTADO DE GARITA

   Este endpoint todavía no existe en Backend 1.7.
   Se conserva preparado para la siguiente etapa.
   ============================================================ */

export function getGateStatus(
  gateId = "gate-01"
) {

  return request(
    `/api/v1/gates/${gateId}/status`,
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


  images.forEach(
    (image) => {

      formData.append(
        "images",
        image
      )
    }
  )


  const response = await fetch(
    `${API_URL}/api/v1/face-profiles/${userId}/enroll`,
    {
      method: "POST",
      body: formData,
    }
  )


  if (!response.ok) {

    const detail = await parseError(
      response,
      "No se pudo registrar el rostro"
    )

    throw new Error(
      typeof detail === "string"
        ? detail
        : JSON.stringify(detail)
    )
  }


  return response.json()
}