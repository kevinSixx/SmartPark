import {
  Activity,
  AlertTriangle,
  Camera,
  CheckCircle2,
  Cloud,
  DoorClosed,
  DoorOpen,
  Gauge,
  History,
  Radio,
  RefreshCw,
  ShieldCheck,
  ShieldX,
  Wifi,
  WifiOff,
  X,
} from "lucide-react"

import {
  useEffect,
  useMemo,
  useState,
} from "react"

import {
  closeGateManually,
  getAccessEvents,
  getBackendHealth,
  getGateActions,
  getUsers,
  getVehicles,
  openGateManually,
} from "../api/smartpark"

import {
  EDGE_URL,
  getEdgeHealth,
  getEdgeStatus,
  getEdgeStreamUrl,
} from "../api/edge"


const GATE_ID = "gate-01"


const stages = [
  [
    "WAITING",
    "Esperando vehículo",
  ],

  [
    "VEHICLE_DETECTED",
    "Vehículo detectado",
  ],

  [
    "TRACKING",
    "Tracking activo",
  ],

  [
    "CROSSING",
    "Entrada / salida",
  ],

  [
    "FACE",
    "Captura de rostro",
  ],

  [
    "PLATE",
    "Captura de placa",
  ],

  [
    "PROCESSING",
    "Procesando en AWS",
  ],

  [
    "RESULT",
    "Decisión",
  ],
]


const manualReasons = [
  "Identidad verificada manualmente",
  "Autorización de seguridad",
  "Visitante autorizado",
  "Error de reconocimiento facial",
  "Error de lectura de placa",
  "Emergencia",
  "Otro",
]


function normalizeDecision(
  value
) {

  const normalized = String(
    value || ""
  ).toUpperCase()


  if (
    normalized === "AUTHORIZED"
  ) {

    return {
      label:
        "ACCESO AUTORIZADO",

      className:
        "authorized",

      icon:
        ShieldCheck,
    }
  }


  if (
    normalized === "REJECTED"
    ||
    normalized === "DENIED"
  ) {

    return {
      label:
        "ACCESO RECHAZADO",

      className:
        "rejected",

      icon:
        ShieldX,
    }
  }


  if (
    normalized === "REVIEW"
  ) {

    return {
      label:
        "REVISIÓN REQUERIDA",

      className:
        "review",

      icon:
        AlertTriangle,
    }
  }


  return {
    label:
      "SIN DECISIÓN",

    className:
      "neutral",

    icon:
      Activity,
  }
}


function translateEventType(
  value
) {

  const normalized = String(
    value || ""
  ).toUpperCase()


  if (
    normalized === "ENTRY"
  ) {
    return "ENTRADA"
  }


  if (
    normalized === "EXIT"
  ) {
    return "SALIDA"
  }


  return "—"
}


function translateReason(
  value
) {

  const text = String(
    value || ""
  ).trim()


  const translations = {

    "Active permission found for user and vehicle":
      "Permiso activo encontrado para el usuario y vehículo",

    "No active permission found for user and vehicle":
      "No existe un permiso activo para el usuario y vehículo",

    "Vehicle not found for detected plate":
      "No se encontró un vehículo para la placa detectada",

    "User not found":
      "Usuario no encontrado",
  }


  return (
    translations[text]
    ||
    text
    ||
    "—"
  )
}


function formatScore(
  value
) {

  if (
    value === null
    ||
    value === undefined
  ) {

    return "—"
  }


  const numeric = Number(
    value
  )


  if (
    Number.isNaN(
      numeric
    )
  ) {

    return "—"
  }


  const percentage = (
    numeric <= 1
      ? numeric * 100
      : numeric
  )


  return (
    `${percentage.toFixed(1)}%`
  )
}


function formatDateTime(
  value
) {

  if (!value) {
    return "—"
  }


  const date = new Date(
    value
  )


  if (
    Number.isNaN(
      date.getTime()
    )
  ) {

    return value
  }


  return new Intl.DateTimeFormat(
    "es-EC",
    {
      dateStyle:
        "short",

      timeStyle:
        "medium",
    }
  ).format(
    date
  )
}


function stageIndex(
  stageValue
) {

  const stage = String(
    stageValue || "WAITING"
  ).toUpperCase()


  if (
    stage.includes("RESULT")
    ||
    stage.includes("AUTHORIZED")
    ||
    stage.includes("REJECT")
  ) {

    return 7
  }


  if (
    stage.includes("PROCESS")
  ) {

    return 6
  }


  if (
    stage.includes("PLATE")
  ) {

    return 5
  }


  if (
    stage.includes("FACE")
  ) {

    return 4
  }


  if (
    stage.includes("ENTRY")
    ||
    stage.includes("EXIT")
    ||
    stage.includes("CROSS")
  ) {

    return 3
  }


  if (
    stage.includes("TRACK")
  ) {

    return 2
  }


  if (
    stage.includes("VEHICLE")
  ) {

    return 1
  }


  return 0
}


function GuardGate() {

  const [
    backend,
    setBackend,
  ] = useState(
    null
  )


  const [
    backendError,
    setBackendError,
  ] = useState(
    ""
  )


  const [
    edgeConnected,
    setEdgeConnected,
  ] = useState(
    false
  )


  const [
    edgeStatus,
    setEdgeStatus,
  ] = useState(
    null
  )


  const [
    edgeError,
    setEdgeError,
  ] = useState(
    ""
  )


  const [
    streamError,
    setStreamError,
  ] = useState(
    false
  )


  const [
    events,
    setEvents,
  ] = useState(
    []
  )


  const [
    users,
    setUsers,
  ] = useState(
    []
  )


  const [
    vehicles,
    setVehicles,
  ] = useState(
    []
  )


  const [
    gateActions,
    setGateActions,
  ] = useState(
    []
  )


  const [
    loadingCloud,
    setLoadingCloud,
  ] = useState(
    true
  )


  const [
    manualModal,
    setManualModal,
  ] = useState(
    false
  )


  const [
    manualReason,
    setManualReason,
  ] = useState(
    ""
  )


  const [
    manualObservation,
    setManualObservation,
  ] = useState(
    ""
  )


  const [
    manualNotice,
    setManualNotice,
  ] = useState(
    ""
  )


  const [
    manualNoticeType,
    setManualNoticeType,
  ] = useState(
    "info"
  )


  const [
    manualBusy,
    setManualBusy,
  ] = useState(
    false
  )


  const streamUrl = (
    getEdgeStreamUrl()
  )


  const usersById = useMemo(
    () => {

      return Object.fromEntries(
        users.map(
          (user) => [
            user.id,
            user,
          ]
        )
      )
    },
    [
      users,
    ]
  )


  const vehiclesById = useMemo(
    () => {

      return Object.fromEntries(
        vehicles.map(
          (vehicle) => [
            vehicle.id,
            vehicle,
          ]
        )
      )
    },
    [
      vehicles,
    ]
  )


  const latestEvent = (
    events[0]
    ||
    null
  )


  const latestDecision = (
    normalizeDecision(
      latestEvent?.decision
    )
  )


  const latestUser = (
    latestEvent?.user_id
      ? usersById[
          latestEvent.user_id
        ]
      : null
  )


  const latestVehicle = (
    latestEvent?.vehicle_id
      ? vehiclesById[
          latestEvent.vehicle_id
        ]
      : null
  )


  const currentStage = String(
    edgeStatus?.stage
    ||
    edgeStatus?.state
    ||
    "WAITING"
  ).toUpperCase()


  const currentStageIndex = (
    stageIndex(
      currentStage
    )
  )


  const edgeEventType = String(
    edgeStatus?.event_type
    ||
    ""
  ).toUpperCase()


  const lastGateAction = (
    gateActions[0]
    ||
    null
  )


  const barrierState = (() => {

    const edgeBarrier = String(
      edgeStatus?.barrier_state
      ||
      ""
    ).toUpperCase()


    if (
      edgeBarrier === "OPEN"
      ||
      edgeBarrier === "CLOSED"
    ) {

      return edgeBarrier
    }


    const lastAction = String(
      lastGateAction?.action
      ||
      ""
    ).toUpperCase()


    if (
      lastAction === "OPEN"
    ) {

      return "OPEN"
    }


    if (
      lastAction === "CLOSE"
    ) {

      return "CLOSED"
    }


    return "UNKNOWN"
  })()


  async function loadCloud() {

    try {

      setLoadingCloud(
        true
      )

      setBackendError(
        ""
      )


      const [
        backendData,
        eventData,
        userData,
        vehicleData,
      ] = await Promise.all([

        getBackendHealth(),

        getAccessEvents(),

        getUsers(),

        getVehicles(),

      ])


      const sortedEvents = [
        ...eventData,
      ].sort(
        (
          first,
          second
        ) => {

          return (
            new Date(
              second.timestamp
            ).getTime()
            -
            new Date(
              first.timestamp
            ).getTime()
          )
        }
      )


      setBackend(
        backendData
      )


      setEvents(
        sortedEvents
      )


      setUsers(
        userData
      )


      setVehicles(
        vehicleData
      )


      try {

        const actionData = (
          await getGateActions(
            GATE_ID,
            20
          )
        )


        setGateActions(
          actionData
        )

      } catch (actionError) {

        console.error(
          "No se pudo cargar gate_actions:",
          actionError
        )
      }

    } catch (error) {

      setBackendError(
        error.message
      )

    } finally {

      setLoadingCloud(
        false
      )
    }
  }


  async function pollEdge() {

    try {

      await getEdgeHealth()


      const status = (
        await getEdgeStatus()
      )


      setEdgeConnected(
        true
      )


      setEdgeStatus(
        status
      )


      setEdgeError(
        ""
      )


      setStreamError(
        false
      )

    } catch {

      setEdgeConnected(
        false
      )


      setEdgeStatus(
        null
      )


      setEdgeError(
        `Edge local no disponible en ${EDGE_URL}`
      )
    }
  }


  useEffect(
    () => {

      loadCloud()

      pollEdge()


      const cloudTimer = setInterval(
        loadCloud,
        7000
      )


      const edgeTimer = setInterval(
        pollEdge,
        1500
      )


      return () => {

        clearInterval(
          cloudTimer
        )


        clearInterval(
          edgeTimer
        )
      }
    },
    []
  )


  function openManualModal() {

    setManualNotice(
      ""
    )


    setManualNoticeType(
      "info"
    )


    setManualReason(
      ""
    )


    setManualObservation(
      ""
    )


    setManualModal(
      true
    )
  }


  async function submitManualOpen(
    event
  ) {

    event.preventDefault()
    if (manualBusy) return


    if (
      !manualReason
    ) {

      setManualNoticeType(
        "error"
      )


      setManualNotice(
        "Selecciona un motivo antes de continuar."
      )


      return
    }


    try {

      setManualBusy(
        true
      )


      setManualNotice(
        ""
      )


      const result = (
        await openGateManually(
          GATE_ID,
          {
            reason:
              manualReason,

            observation:
              manualObservation
              ||
              null,

            accessEventId:
              latestEvent?.id
              ||
              null,
          }
        )
      )


      if (
        result?.status
        === "SUCCESS"
      ) {

        setManualNoticeType(
          "success"
        )


        setManualNotice(
          "Barrera abierta correctamente. La acción quedó registrada en RDS."
        )

      } else {

        setManualNoticeType(
          "error"
        )


        setManualNotice(
          "La acción se registró, pero la apertura no pudo completarse. Inténtalo nuevamente."
        )
      }


      setManualModal(
        false
      )


      await loadCloud()

    } catch (error) {

      setManualNoticeType(
        "error"
      )


      setManualNotice(
        error.message
      )

    } finally {

      setManualBusy(
        false
      )
    }
  }


  async function requestManualClose() {

    if (manualBusy) return

    const confirmed = window.confirm(
      "¿Cerrar manualmente la barrera de Garita 01?"
    )


    if (
      !confirmed
    ) {

      return
    }


    try {

      setManualBusy(
        true
      )


      setManualNotice(
        ""
      )


      const result = (
        await closeGateManually(
          GATE_ID,
          {
            observation:
              "Cierre manual desde la interfaz de guardia",

            accessEventId:
              latestEvent?.id
              ||
              null,
          }
        )
      )


      if (
        result?.status
        === "SUCCESS"
      ) {

        setManualNoticeType(
          "success"
        )


        setManualNotice(
          "Barrera cerrada correctamente. La acción quedó registrada en RDS."
        )

      } else {

        setManualNoticeType(
          "error"
        )


        setManualNotice(
          "La acción se registró, pero el cierre no pudo completarse. Inténtalo nuevamente."
        )
      }


      await loadCloud()

    } catch (error) {

      setManualNoticeType(
        "error"
      )


      setManualNotice(
        error.message
      )

    } finally {

      setManualBusy(
        false
      )
    }
  }


  return (
    <section
      className="
        guard-page
        guard-page-v2
      "
    >

      <div
        className="
          guard-heading
          guard-heading-v2
        "
      >

        <div>

          <p className="eyebrow">
            Centro de control operativo
          </p>


          <div className="guard-title-row">

            <h2>
              Garita 01
            </h2>


            <span
              className={
                `guard-system-pill ${
                  backend?.status
                  ===
                  "ok"
                    ? "online"
                    : "offline"
                }`
              }
            >

              <span />

              {
                backend?.status
                ===
                "ok"
                  ? "AWS EN LÍNEA"
                  : "AWS SIN CONEXIÓN"
              }

            </span>

          </div>


          <p>
            Supervisión del Edge local,
            autorización en AWS y control
            de barrera.
          </p>

        </div>


        <button
          className="secondary-button"
          type="button"
          onClick={
            () => {

              loadCloud()

              pollEdge()
            }
          }
        >

          <RefreshCw
            size={18}
          />

          Actualizar

        </button>

      </div>


      {
        (
          backendError
          ||
          (
            edgeError
            &&
            !edgeConnected
          )
        )
        &&
        (

          <div
            className="
              guard-alert-stack
              compact-alert-stack
            "
          >

            {
              backendError
              &&
              (

                <div
                  className="
                    alert
                    error
                  "
                >
                  AWS Backend:
                  {" "}
                  {backendError}
                </div>
              )
            }


            {
              edgeError
              &&
              (

                <div
                  className="
                    alert
                    info
                  "
                >

                  Edge local pendiente.

                  {" "}

                  Cuando conectemos
                  el servicio local de
                  Garita 01 aparecerán
                  aquí el video, sensor,
                  tracking y estados en
                  tiempo real.

                </div>
              )
            }

          </div>
        )
      }


      <div className="guard-health-strip">

        <div
          className={
            edgeConnected
              ? "health-dot-card online"
              : "health-dot-card offline"
          }
        >

          {
            edgeConnected
              ? (
                <Wifi size={18} />
              )
              : (
                <WifiOff size={18} />
              )
          }

          <span>
            Edge
          </span>

          <strong>
            {
              edgeConnected
                ? "Conectado"
                : "Pendiente"
            }
          </strong>

        </div>


        <div
          className={
            backend?.status
            ===
            "ok"
              ? "health-dot-card online"
              : "health-dot-card offline"
          }
        >

          <Cloud
            size={18}
          />

          <span>
            Backend AWS
          </span>

          <strong>
            {
              loadingCloud
                ? "Consultando"
                : backend?.version
                  || "Sin conexión"
            }
          </strong>

        </div>


        <div className="health-dot-card neutral">

          <Radio
            size={18}
          />

          <span>
            Sensor HC-SR04
          </span>

          <strong>
            {
              edgeConnected
                ? edgeStatus?.sensor
                  || "Esperando"
                : "Sin telemetría"
            }
          </strong>

        </div>


        <div
          className={
            `health-dot-card ${
              barrierState
              ===
              "OPEN"
                ? "warning"
                : "neutral"
            }`
          }
        >

          {
            barrierState
            ===
            "OPEN"
              ? (
                <DoorOpen
                  size={18}
                />
              )
              : (
                <DoorClosed
                  size={18}
                />
              )
          }

          <span>
            Barrera
          </span>

          <strong>
            {
              barrierState
              ===
              "OPEN"
                ? "ABIERTA"
                : barrierState
                  ===
                  "CLOSED"
                    ? "CERRADA"
                    : "SIN TELEMETRÍA"
            }
          </strong>

        </div>

      </div>


      <div className="guard-operations-grid">

        <article
          className="
            guard-camera-panel
            guard-camera-panel-v2
          "
        >

          <div className="guard-panel-title">

            <div>

              <span
                className={
                  `live-dot ${
                    edgeConnected
                      ? "active"
                      : ""
                  }`
                }
              />


              <div>

                <strong>
                  Cámara · Garita 01
                </strong>

                <small>
                  Video procesado por
                  YOLO11n + ByteTrack
                  en el Edge
                </small>

              </div>

            </div>


            <span className="guard-chip">

              {
                edgeConnected
                  ? "EN VIVO"
                  : "ESPERANDO EDGE"
              }

            </span>

          </div>


          <div
            className="
              guard-camera-frame
              guard-camera-frame-v2
            "
          >

            {
              edgeConnected
              &&
              !streamError
                ? (

                  <img
                    src={streamUrl}
                    alt="
                      Video procesado
                      de Garita 01
                    "
                    onError={
                      () =>
                        setStreamError(
                          true
                        )
                    }
                  />

                )
                : (

                  <div
                    className="
                      guard-camera-placeholder
                      guard-camera-placeholder-v2
                    "
                  >

                    <Camera
                      size={48}
                    />

                    <strong>
                      Garita preparada
                      para video local
                    </strong>

                    <p>
                      Aquí aparecerá la
                      vista del Edge con
                      vehículo, bounding
                      box, Track ID y
                      línea de control.
                    </p>

                  </div>
                )
            }


            <div
              className="
                guard-camera-overlay
                top-left
              "
            >

              {
                edgeConnected
                  ? "EDGE ONLINE"
                  : "EDGE OFFLINE"
              }

            </div>


            <div
              className="
                guard-camera-overlay
                bottom-left
              "
            >

              {
                edgeConnected
                  ? (
                    translateEventType(
                      edgeEventType
                    )
                    ===
                    "—"
                      ? "ESPERANDO VEHÍCULO"
                      : translateEventType(
                          edgeEventType
                        )
                  )
                  : "ESPERANDO EDGE"
              }

            </div>

          </div>

        </article>


        <aside className="guard-control-column">

          <article
            className="
              guard-access-panel
              guard-access-panel-v2
            "
          >

            <div className="guard-panel-title">

              <div>

                <Activity
                  size={19}
                />


                <div>

                  <strong>
                    Flujo automático
                  </strong>

                  <small>
                    Estado actual
                    del proceso
                  </small>

                </div>

              </div>

            </div>


            <div
              className="
                guard-stage-current
                guard-stage-current-v2
              "
            >

              <span>
                ETAPA ACTUAL
              </span>

              <strong>

                {
                  edgeConnected
                    ? currentStage
                        .replaceAll(
                          "_",
                          " "
                        )
                    : "ESPERANDO EDGE"
                }

              </strong>

            </div>


            <div
              className="
                guard-flow-list
                compact-flow-list
              "
            >

              {
                stages.map(
                  (
                    [
                      key,
                      label,
                    ],
                    index
                  ) => {

                    const isDone = (
                      currentStageIndex
                      >
                      index
                    )


                    const isActive = (
                      currentStageIndex
                      ===
                      index
                    )


                    return (

                      <div
                        className={
                          `guard-flow-step ${
                            isDone
                              ? "done"
                              : ""
                          } ${
                            isActive
                              ? "active"
                              : ""
                          }`
                        }
                        key={key}
                      >

                        <span className="guard-flow-index">

                          {
                            isDone
                              ? (
                                <CheckCircle2
                                  size={15}
                                />
                              )
                              : (
                                index + 1
                              )
                          }

                        </span>


                        <span>
                          {label}
                        </span>

                      </div>
                    )
                  }
                )
              }

            </div>

          </article>


          <article className="guard-current-result-card">

            <div className="guard-current-result-header">

              <span>
                Último resultado AWS
              </span>


              <strong
                className={
                  latestDecision
                    .className
                }
              >

                {
                  latestDecision
                    .label
                }

              </strong>

            </div>


            <div className="guard-current-result-data">

              <div>

                <span>
                  Persona
                </span>

                <strong>
                  {
                    latestUser?.name
                    ||
                    "No identificada"
                  }
                </strong>

              </div>


              <div>

                <span>
                  Placa
                </span>

                <strong>
                  {
                    latestEvent
                      ?.detected_plate
                    ||
                    latestVehicle
                      ?.plate
                    ||
                    "—"
                  }
                </strong>

              </div>


              <div>

                <span>
                  Movimiento
                </span>

                <strong>
                  {
                    translateEventType(
                      latestEvent
                        ?.event_type
                    )
                  }
                </strong>

              </div>


              <div>

                <span>
                  Rostro
                </span>

                <strong>
                  {
                    formatScore(
                      latestEvent
                        ?.face_score
                    )
                  }
                </strong>

              </div>


              <div>

                <span>
                  OCR
                </span>

                <strong>
                  {
                    formatScore(
                      latestEvent
                        ?.plate_score
                    )
                  }
                </strong>

              </div>


              <div className="wide">

                <span>
                  Motivo
                </span>

                <strong>
                  {
                    translateReason(
                      latestEvent
                        ?.reason
                    )
                  }
                </strong>

              </div>

            </div>

          </article>

        </aside>

      </div>


      <div className="guard-lower-grid">

        <article
          className="
            panel
            guard-recent-panel
            guard-recent-panel-v2
          "
        >

          <div className="panel-header">

            <div>

              <h3>
                Eventos recientes
              </h3>

              <p>
                Últimos accesos
                registrados en RDS.
              </p>

            </div>


            <History
              size={20}
            />

          </div>


          <div className="guard-events-list">

            {
              events
                .slice(
                  0,
                  6
                )
                .map(
                  (
                    event
                  ) => {

                    const decision = (
                      normalizeDecision(
                        event.decision
                      )
                    )


                    const user = (
                      event.user_id
                        ? usersById[
                            event.user_id
                          ]
                        : null
                    )


                    return (

                      <div
                        className="guard-event-row"
                        key={
                          event.id
                        }
                      >

                        <div className="guard-event-time">

                          <strong>
                            {
                              translateEventType(
                                event.event_type
                              )
                            }
                          </strong>

                          <span>
                            {
                              formatDateTime(
                                event.timestamp
                              )
                            }
                          </span>

                        </div>


                        <div className="guard-event-person">

                          <strong>
                            {
                              user?.name
                              ||
                              "No identificada"
                            }
                          </strong>

                          <span>
                            {
                              event.detected_plate
                              ||
                              "Sin placa"
                            }
                          </span>

                        </div>


                        <span
                          className={
                            `guard-table-decision ${
                              decision.className
                            }`
                          }
                        >

                          {
                            decision.label
                              .replace(
                                "ACCESO ",
                                ""
                              )
                          }

                        </span>

                      </div>
                    )
                  }
                )
            }

          </div>

        </article>


        <article
          className="
            panel
            guard-manual-panel
            guard-manual-panel-v2
          "
        >

          <div className="panel-header">

            <div>

              <h3>
                Control de barrera
              </h3>

              <p>
                Operación manual con
                auditoría del guardia.
              </p>

            </div>


            <Gauge
              size={20}
            />

          </div>


          <div className="barrier-state-box">

            <span>
              Estado según última acción
            </span>

            <strong>

              {
                barrierState
                ===
                "OPEN"
                  ? "BARRERA ABIERTA"
                  : barrierState
                    ===
                    "CLOSED"
                      ? "BARRERA CERRADA"
                      : "SIN INFORMACIÓN"
              }

            </strong>


            {
              lastGateAction
              &&
              (

                <small>

                  Última acción:
                  {" "}
                  {
                    lastGateAction
                      .action
                  }
                  {" · "}
                  {
                    lastGateAction
                      .source
                  }
                  {" · "}
                  {
                    formatDateTime(
                      lastGateAction
                        .timestamp
                    )
                  }

                </small>
              )
            }

          </div>


          <div className="guard-manual-actions">

            <button
              type="button"
              className="
                primary-button
                gate-open-button
              "
              onClick={
                openManualModal
              }
              disabled={
                manualBusy
              }
            >

              <DoorOpen
                size={19}
              />

              Abrir manualmente

            </button>


            <button
              type="button"
              className="danger-outline-button"
              onClick={
                requestManualClose
              }
              disabled={
                manualBusy
              }
            >

              <DoorClosed
                size={19}
              />

              Cerrar barrera

            </button>

          </div>


          {
            manualNotice
            &&
            (

              <div
                className={
                  `alert ${
                    manualNoticeType
                  }`
                }
              >

                {
                  manualNotice
                }

              </div>
            )
          }


          <p className="guard-manual-help">

            La apertura exige
            justificación y queda
            vinculada automáticamente
            al guardia autenticado
            mediante JWT.

          </p>

        </article>

      </div>


      {
        manualModal
        &&
        (

          <div className="modal-backdrop">

            <form
              className="
                modal-card
                guard-manual-modal
                guard-manual-modal-v2
              "
              onSubmit={
                submitManualOpen
              }
            >

              <div className="modal-header">

                <div>

                  <p className="eyebrow">
                    Control excepcional
                  </p>

                  <h3>
                    Abrir barrera
                    manualmente
                  </h3>

                </div>


                <button
                  type="button"
                  className="icon-button"
                  onClick={
                    () =>
                      setManualModal(
                        false
                      )
                  }
                >

                  <X
                    size={20}
                  />

                </button>

              </div>


              <div className="modal-warning-box">

                Esta acción enviará
                OPEN al Backend 1.7,
                que publicará el comando
                en AWS IoT Core.

                La acción quedará
                auditada en RDS.

              </div>


              <label>

                <span>
                  Motivo *
                </span>

                <select
                  value={
                    manualReason
                  }
                  onChange={
                    (
                      event
                    ) =>
                      setManualReason(
                        event
                          .target
                          .value
                      )
                  }
                >

                  <option value="">
                    Selecciona un motivo
                  </option>


                  {
                    manualReasons.map(
                      (
                        reason
                      ) => (

                        <option
                          key={
                            reason
                          }
                          value={
                            reason
                          }
                        >
                          {
                            reason
                          }
                        </option>
                      )
                    )
                  }

                </select>

              </label>


              <label>

                <span>
                  Observación
                </span>

                <textarea
                  value={
                    manualObservation
                  }
                  onChange={
                    (
                      event
                    ) =>
                      setManualObservation(
                        event
                          .target
                          .value
                      )
                  }
                  rows="4"
                  placeholder="
                    Describe brevemente
                    la verificación realizada...
                  "
                />

              </label>


              {
                manualNotice
                &&
                (

                  <div
                    className={
                      `alert ${
                        manualNoticeType
                      }`
                    }
                  >

                    {
                      manualNotice
                    }

                  </div>
                )
              }


              <div className="modal-actions">

                <button
                  type="button"
                  className="secondary-button"
                  onClick={
                    () =>
                      setManualModal(
                        false
                      )
                  }
                >

                  Cancelar

                </button>


                <button
                  type="submit"
                  className="primary-button"
                  disabled={
                    manualBusy
                  }
                >

                  <DoorOpen
                    size={18}
                  />

                  {
                    manualBusy
                      ? "Enviando..."
                      : "Confirmar apertura"
                  }

                </button>

              </div>

            </form>

          </div>
        )
      }

    </section>
  )
}


export default GuardGate
