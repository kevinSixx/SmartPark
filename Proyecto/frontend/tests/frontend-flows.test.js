import assert from "node:assert/strict"
import test from "node:test"

import {
  faceFileSignature,
  loadUserFaceState,
  validateFaceFile,
  validateFaceImageCount,
} from "../src/utils/faceEnrollment.js"
import { loginErrorMessage, validateLogin } from "../src/utils/loginValidation.js"
import { enrollFace, getFaceProfile, getStaffAccounts, getUsers } from "../src/api/smartpark.js"

const user = { id: 4, name: "Kevin Rueda", institutional_id: "UCE-004" }
const notFound = Object.assign(new Error("internal backend text"), { status: 404 })

test("el 404 del perfil conserva el usuario y muestra sin biometría", async () => {
  const state = await loadUserFaceState(4, async () => user, async () => { throw notFound })
  assert.deepEqual(state, { user, hasProfile: false, profileError: null })
})

test("el perfil existente queda registrado y otros errores son visibles sin perder el usuario", async () => {
  const registered = await loadUserFaceState(4, async () => user, async () => ({ user_id: 4 }))
  assert.equal(registered.hasProfile, true)
  const unavailable = Object.assign(new Error("Servicio temporalmente no disponible"), { status: 503 })
  const failed = await loadUserFaceState(4, async () => user, async () => { throw unavailable })
  assert.equal(failed.user.name, "Kevin Rueda")
  assert.equal(failed.profileError.status, 503)
})

test("un usuario inexistente bloquea la carga antes de consultar el perfil", async () => {
  let profileCalled = false
  await assert.rejects(loadUserFaceState(999, async () => { throw notFound }, async () => {
    profileCalled = true
  }), { status: 404 })
  assert.equal(profileCalled, false)
})

test("cantidad de fotos: 1, 2, 3, 5 y más de 5", () => {
  for (const count of [1, 2]) assert.match(validateFaceImageCount(count), /al menos 3/)
  for (const count of [3, 5]) assert.equal(validateFaceImageCount(count), "")
  assert.match(validateFaceImageCount(6), /hasta 5/)
})

test("tipo, tamaño y duplicados de imágenes", () => {
  const jpg = { name: "uno.jpg", type: "image/jpeg", size: 1000, lastModified: 1 }
  assert.equal(validateFaceFile(jpg, new Set()), "")
  assert.equal(validateFaceFile({ ...jpg, type: "image/png" }, new Set()), "")
  assert.equal(validateFaceFile({ ...jpg, type: "image/webp" }, new Set()), "")
  assert.match(validateFaceFile({ ...jpg, type: "text/plain" }, new Set()), /formato permitido/)
  assert.match(validateFaceFile({ ...jpg, size: 10 * 1024 * 1024 + 1 }, new Set()), /10 MB/)
  assert.match(validateFaceFile(jpg, new Set([faceFileSignature(jpg)])), /ya está seleccionada/)
})

test("validaciones y errores de login", () => {
  assert.equal(validateLogin("", "123456"), "Ingresa tu usuario.")
  assert.equal(validateLogin("admin", ""), "Ingresa tu contraseña.")
  assert.match(validateLogin("admin", "12345"), /al menos 6/)
  assert.equal(validateLogin("admin", "123456"), "")
  assert.equal(loginErrorMessage(401), "Usuario o contraseña incorrectos.")
  assert.match(loginErrorMessage(0), /No se pudo conectar/)
  assert.match(loginErrorMessage(503), /No se pudo conectar/)
  assert.match(loginErrorMessage(422), /Ocurrió un problema/)
})

test("API: lista vacía y 204 son éxitos", async () => {
  const previousFetch = globalThis.fetch
  try {
    globalThis.fetch = async () => new Response("[]", { status: 200 })
    assert.deepEqual(await getUsers(), [])
    globalThis.fetch = async () => new Response(null, { status: 204 })
    assert.equal(await getFaceProfile(4), null)
  } finally {
    globalThis.fetch = previousFetch
  }
})

test("API: errores 400, 401, 403, 404, 422 y 5xx no exponen JSON", async () => {
  const previousFetch = globalThis.fetch
  try {
    for (const status of [400, 401, 403, 404, 422, 500, 502, 503]) {
      globalThis.fetch = async () => new Response(JSON.stringify({ detail: [{ type: "pydantic_error", msg: "Internal traceback" }] }), {
        status, headers: { "Content-Type": "application/json" },
      })
      await assert.rejects(getFaceProfile(4), (error) => {
        assert.equal(error.status, status)
        assert.doesNotMatch(error.message, /pydantic|traceback|\[\{|JSON/i)
        return true
      })
    }
  } finally {
    globalThis.fetch = previousFetch
  }
})

test("API: error de IA sin rostro y fallo de red tienen mensajes seguros", async () => {
  const previousFetch = globalThis.fetch
  try {
    globalThis.fetch = async () => new Response(JSON.stringify({ detail: "Face not detected in image" }), { status: 400 })
    await assert.rejects(enrollFace(4, []), /No se detectó un rostro válido/)
    globalThis.fetch = async () => { throw new TypeError("secret network internals") }
    await assert.rejects(getUsers(), (error) => error.status === 0 && !error.message.includes("secret"))
  } finally {
    globalThis.fetch = previousFetch
  }
})

test("API: enrolamiento de 3 y 5 fotos envía cada muestra y recibe dimensiones", async () => {
  const previousFetch = globalThis.fetch
  try {
    for (const count of [3, 5]) {
      globalThis.fetch = async (_url, options) => {
        assert.equal(options.method, "POST")
        assert.equal(options.body.get("user_id"), "4")
        assert.equal(options.body.getAll("images").length, count)
        return new Response(JSON.stringify({ samples_used: count, embedding_dimension: 512 }), { status: 201 })
      }
      const photos = Array.from({ length: count }, () => new Blob(["image"], { type: "image/jpeg" }))
      const result = await enrollFace(4, photos)
      assert.equal(result.samples_used, count)
      assert.equal(result.embedding_dimension, 512)
    }
  } finally {
    globalThis.fetch = previousFetch
  }
})

test("API: 401 autenticado borra la sesión", async () => {
  const previousFetch = globalThis.fetch
  const previousStorage = globalThis.localStorage
  let cleared = false
  try {
    globalThis.localStorage = { getItem: () => '{"accessToken":"test"}', removeItem: () => { cleared = true } }
    globalThis.fetch = async () => new Response(JSON.stringify({ detail: "Unauthorized" }), { status: 401 })
    await assert.rejects(getStaffAccounts(), (error) => error.status === 401)
    assert.equal(cleared, true)
  } finally {
    globalThis.fetch = previousFetch
    globalThis.localStorage = previousStorage
  }
})
