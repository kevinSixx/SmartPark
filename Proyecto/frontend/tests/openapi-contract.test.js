import assert from "node:assert/strict"
import { readFileSync, readdirSync } from "node:fs"
import test from "node:test"

import * as api from "../src/api/smartpark.js"

// The operation IDs identify the intended operation; paths, methods and schemas
// are read from the production OpenAPI instead of copied from the frontend.
const spec = JSON.parse(readFileSync(new URL("../../docs/smartpark-openapi-production.json", import.meta.url), "utf8"))
const photo = new Blob(["photo"], { type: "image/jpeg" })
const cases = [
  ["getBackendHealth", "health_health_get", () => api.getBackendHealth()],
  ["loginStaff", "login_api_v1_auth_login_post", () => api.loginStaff("admin", "password")],
  ["getCurrentStaff", "me_api_v1_auth_me_get", () => api.getCurrentStaff()],
  ["getStaffAccounts", "list_staff_api_v1_staff_get", () => api.getStaffAccounts()],
  ["getStaffAccount", "get_staff_api_v1_staff__staff_id__get", () => api.getStaffAccount(2)],
  ["createStaffAccount", "create_staff_api_v1_staff_post", () => api.createStaffAccount({ full_name: "Test Guard", username: "testguard", password: "password", role: "GUARD", active: true })],
  ["updateStaffAccount", "update_staff_api_v1_staff__staff_id__patch", () => api.updateStaffAccount(2, { active: false })],
  ["getUsers", "read_users_api_v1_users_get", () => api.getUsers()],
  ["getUser", "read_user_api_v1_users__user_id__get", () => api.getUser(4)],
  ["createUser", "register_user_api_v1_users_post", () => api.createUser({ name: "Test User", institutional_id: "UCE-004" })],
  ["getVehicles", "read_vehicles_api_v1_vehicles_get", () => api.getVehicles()],
  ["createVehicle", "register_vehicle_api_v1_vehicles_post", () => api.createVehicle({ user_id: 4, plate: "PAA1234", brand: "Kia", model: "Rio", color: "White", status: "ACTIVE" })],
  ["getPermissions", "read_permissions_api_v1_permissions_get", () => api.getPermissions()],
  ["createPermission", "register_permission_api_v1_permissions_post", () => api.createPermission({ user_id: 4, vehicle_id: 7, valid_from: "2026-09-29T00:00:00Z", valid_to: "2026-10-29T00:00:00Z", active: true })],
  ["getAccessEvents", "read_access_events_api_v1_access_events_get", () => api.getAccessEvents()],
  ["processAccess", "process_access_api_v1_access_process_post", () => api.processAccess(photo, photo, "ENTRY")],
  ["openGateManually", "open_gate_api_v1_gates__gate_id__open_post", () => api.openGateManually("gate-01", { reason: "MANUAL_CHECK", observation: "Test", accessEventId: 3 })],
  ["closeGateManually", "close_gate_api_v1_gates__gate_id__close_post", () => api.closeGateManually("gate-01", { observation: "Test", accessEventId: 3 })],
  ["getGateActions", "get_gate_actions_api_v1_gates__gate_id__actions_get", () => api.getGateActions("gate-01", 100)],
  ["getFaceProfile", "read_face_profile_api_v1_face_profiles__user_id__get", () => api.getFaceProfile(4)],
  ["enrollFace", "enroll_api_v1_face_profiles_enroll_post", () => api.enrollFace(4, [photo, photo, photo])],
]

function operationById(id) {
  for (const [path, methods] of Object.entries(spec.paths)) {
    for (const [method, operation] of Object.entries(methods)) {
      if (operation.operationId === id) return { path, method: method.toUpperCase(), operation }
    }
  }
  assert.fail(`Operation ID missing from production OpenAPI: ${id}`)
}

function resolveSchema(ref) {
  assert.ok(ref?.startsWith("#/components/schemas/"), `Unsupported schema reference: ${ref}`)
  return spec.components.schemas[ref.split("/").at(-1)]
}

function assertRequest(name, id, url, options = {}) {
  const { path, method, operation } = operationById(id)
  const actual = new URL(url, "http://localhost")
  const routePattern = new RegExp(`^${path.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/\\\{[^}]+\\\}/g, "[^/]+")}$`)
  assert.match(actual.pathname, routePattern, `${name}: path must match OpenAPI ${path}`)
  assert.equal(options.method || "GET", method, `${name}: HTTP method`)

  const params = operation.parameters || []
  const allowedQuery = new Set(params.filter((param) => param.in === "query").map((param) => param.name))
  for (const key of actual.searchParams.keys()) assert.ok(allowedQuery.has(key), `${name}: unexpected query parameter ${key}`)
  for (const param of params.filter((item) => item.in === "query" && item.required)) {
    assert.ok(actual.searchParams.has(param.name), `${name}: missing query parameter ${param.name}`)
  }
  for (const param of params.filter((item) => item.in === "query" && actual.searchParams.has(item.name))) {
    const value = actual.searchParams.get(param.name)
    if (param.schema?.type === "integer") {
      assert.match(value, /^\d+$/, `${name}: ${param.name} must be integer`)
      if (param.schema.minimum !== undefined) assert.ok(Number(value) >= param.schema.minimum)
      if (param.schema.maximum !== undefined) assert.ok(Number(value) <= param.schema.maximum)
    }
  }

  const headers = new Headers(options.headers || {})
  const secured = Boolean(operation.security?.some((item) => Object.hasOwn(item, "HTTPBearer")))
  assert.equal(headers.get("Authorization"), secured ? "Bearer contract-token" : null, `${name}: Bearer security`)

  const requestBody = operation.requestBody
  if (!requestBody) {
    assert.equal(options.body, undefined, `${name}: unexpected body`)
    return
  }
  const contentType = Object.keys(requestBody.content)[0]
  const schema = resolveSchema(requestBody.content[contentType].schema.$ref)
  let keys
  if (contentType === "multipart/form-data") {
    assert.ok(options.body instanceof FormData, `${name}: multipart FormData required`)
    assert.equal(headers.get("Content-Type"), null, `${name}: browser must set multipart boundary`)
    keys = [...options.body.keys()]
    if (name === "enrollFace") {
      assert.equal(options.body.get("user_id"), "4")
      assert.equal(options.body.getAll("images").length, 3)
    }
  } else {
    assert.equal(contentType, "application/json")
    assert.match(headers.get("Content-Type") || "", /application\/json/i)
    keys = Object.keys(JSON.parse(options.body))
  }
  for (const key of keys) assert.ok(Object.hasOwn(schema.properties, key), `${name}: undocumented body field ${key}`)
  for (const key of schema.required || []) assert.ok(keys.includes(key), `${name}: missing required body field ${key}`)
}

test("every SmartPark helper is covered by the production OpenAPI contract test", () => {
  const exports = Object.keys(api).filter((name) => name !== "API_URL")
  assert.deepEqual(exports.sort(), cases.map(([name]) => name).sort())
})

test("the former user-specific face enrollment route is rejected by production OpenAPI", () => {
  assert.throws(() => assertRequest("enrollFace", "enroll_api_v1_face_profiles_enroll_post", "/api/v1/face-profiles/4/enroll", { method: "POST" }), /path must match OpenAPI/)
})

test("all SmartPark methods, paths, query, body format, fields, auth and success codes match production OpenAPI", async () => {
  const previousFetch = globalThis.fetch
  const previousStorage = globalThis.localStorage
  try {
    globalThis.localStorage = { getItem: () => JSON.stringify({ accessToken: "contract-token" }), removeItem: () => {} }
    for (const [name, id, invoke] of cases) {
      let calls = 0
      globalThis.fetch = async (url, options) => {
        calls++
        assertRequest(name, id, url, options)
        const { operation } = operationById(id)
        const successCode = Number(Object.keys(operation.responses).find((code) => code.startsWith("2")))
        assert.ok(successCode, `${name}: no documented success response`)
        return new Response(successCode === 204 ? null : "{}", { status: successCode, headers: { "Content-Type": "application/json" } })
      }
      await invoke()
      assert.equal(calls, 1, `${name}: one HTTP request expected`)
    }
  } finally {
    globalThis.fetch = previousFetch
    globalThis.localStorage = previousStorage
  }
})

test("no Backend fetch bypasses the audited API module", () => {
  const sourceDir = new URL("../src/", import.meta.url)
  function visit(directory) {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const path = new URL(entry.name + (entry.isDirectory() ? "/" : ""), directory)
      if (entry.isDirectory()) visit(path)
      else if (/\.[jt]sx?$/.test(entry.name) && !["smartpark.js", "edge.js"].includes(entry.name)) {
        assert.doesNotMatch(readFileSync(path, "utf8"), /\bfetch\s*\(|\baxios\b|\bXMLHttpRequest\b/, `${path.pathname}: direct HTTP call needs audit`)
      }
    }
  }
  visit(sourceDir)
})
