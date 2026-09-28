const EDGE_URL =
  import.meta.env.VITE_EDGE_URL ||
  "http://127.0.0.1:9000"

const EDGE_STREAM_URL =
  import.meta.env.VITE_EDGE_STREAM_URL ||
  `${EDGE_URL}/video`

async function edgeRequest(path, timeoutMs = 1200) {
  const controller = new AbortController()
  const timer = setTimeout(
    () => controller.abort(),
    timeoutMs
  )

  try {
    const response = await fetch(
      `${EDGE_URL}${path}`,
      {
        signal: controller.signal,
        cache: "no-store",
      }
    )

    if (!response.ok) {
      throw new Error(
        `Edge respondió ${response.status}`
      )
    }

    return response.json()
  } finally {
    clearTimeout(timer)
  }
}

export function getEdgeHealth() {
  return edgeRequest("/health")
}

export function getEdgeStatus() {
  return edgeRequest("/status")
}

export function getEdgeStreamUrl() {
  return EDGE_STREAM_URL
}

export {
  EDGE_URL,
  EDGE_STREAM_URL,
}
