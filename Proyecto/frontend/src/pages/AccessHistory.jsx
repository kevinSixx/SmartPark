import {
  Car,
  History,
  LogIn,
  RefreshCw,
  ShieldCheck,
  ShieldX,
  UserRound,
} from "lucide-react"

import {
  useEffect,
  useMemo,
  useState,
} from "react"

import {
  getAccessEvents,
  getUsers,
  getVehicles,
} from "../api/smartpark"


function AccessHistory() {

  const [events, setEvents] =
    useState([])

  const [users, setUsers] =
    useState([])

  const [vehicles, setVehicles] =
    useState([])

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState("")


  /* ==========================================================
     MAPA DE USUARIOS
     ========================================================== */

  const usersById =
    useMemo(
      () => {

        const map = {}

        users.forEach(
          (user) => {

            map[user.id] =
              user

          }
        )

        return map

      },
      [users]
    )


  /* ==========================================================
     MAPA DE VEHÍCULOS
     ========================================================== */

  const vehiclesById =
    useMemo(
      () => {

        const map = {}

        vehicles.forEach(
          (vehicle) => {

            map[vehicle.id] =
              vehicle

          }
        )

        return map

      },
      [vehicles]
    )


  /* ==========================================================
     CARGAR DATOS
     ========================================================== */

  async function loadData() {

    try {

      setLoading(true)
      setError("")


      const [
        eventsData,
        usersData,
        vehiclesData,
      ] = await Promise.all([
        getAccessEvents(),
        getUsers(),
        getVehicles(),
      ])


      /*
       * Mostramos primero
       * los eventos más recientes.
       */

      const sortedEvents =
        [...eventsData].sort(
          (a, b) => {

            const dateA =
              new Date(
                a.timestamp
              ).getTime()

            const dateB =
              new Date(
                b.timestamp
              ).getTime()

            return dateB - dateA

          }
        )


      setEvents(
        sortedEvents
      )

      setUsers(
        usersData
      )

      setVehicles(
        vehiclesData
      )


    } catch (err) {

      setError(
        err.message
      )

    } finally {

      setLoading(false)

    }
  }


  useEffect(
    () => {

      loadData()

    },
    []
  )


  /* ==========================================================
     FORMATO FECHA
     ========================================================== */

  function formatDateTime(
    value
  ) {

    if (!value) {

      return "—"
    }


    const date =
      new Date(value)


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
          "medium",

        timeStyle:
          "medium",
      }
    ).format(date)
  }


  /* ==========================================================
     FORMATO SCORE
     ========================================================== */

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


    const number =
      Number(value)


    if (
      Number.isNaN(number)
    ) {

      return "—"
    }


    /*
     * Normalmente nuestros scores
     * están entre 0 y 1.
     */

    const percentage =
      number <= 1
        ? number * 100
        : number


    return (
      `${percentage.toFixed(1)}%`
    )
  }


  /* ==========================================================
     ESTADO DECISIÓN
     ========================================================== */

  function getDecisionInfo(
    decision
  ) {

    const normalized =
      String(
        decision || ""
      ).toUpperCase()


    if (
      normalized
      ===
      "AUTHORIZED"
    ) {

      return {
        label:
          "AUTORIZADO",

        className:
          "permission-state valid",
      }
    }


    if (
      normalized
      ===
      "DENIED"
      ||
      normalized
      ===
      "REJECTED"
    ) {

      return {
        label:
          "DENEGADO",

        className:
          "permission-state expired",
      }
    }


    return {
      label:
        normalized
        ||
        "DESCONOCIDO",

      className:
        "permission-state inactive",
    }
  }


  /* ==========================================================
     ESTADO EVENTO
     ========================================================== */

  function getEventInfo(
    eventType
  ) {

    const normalized =
      String(
        eventType || ""
      ).toUpperCase()


    if (
      normalized
      ===
      "ENTRY"
    ) {

      return {
        label:
          "ENTRADA",

        className:
          "permission-state scheduled",
      }
    }


    if (
      normalized
      ===
      "EXIT"
    ) {

      return {
        label:
          "SALIDA",

        className:
          "permission-state inactive",
      }
    }


    return {
      label:
        normalized
        ||
        "—",

      className:
        "permission-state inactive",
    }
  }


  /* ==========================================================
     CONTADORES
     ========================================================== */

  const authorizedCount =
    events.filter(
      (event) =>
        String(
          event.decision
        ).toUpperCase()
        ===
        "AUTHORIZED"
    ).length


  const deniedCount =
    events.filter(
      (event) =>
        (
          String(
            event.decision
          ).toUpperCase()
          ===
          "DENIED"
          ||
          String(
            event.decision
          ).toUpperCase()
          ===
          "REJECTED"
        )
    ).length


  const entryCount =
    events.filter(
      (event) =>
        String(
          event.event_type
        ).toUpperCase()
        ===
        "ENTRY"
    ).length


  /* ==========================================================
     INTERFAZ
     ========================================================== */

  return (
    <section>

      {/* ======================================================
          ENCABEZADO
          ====================================================== */}

      <div className="page-heading row-heading">

        <div>

          <p className="eyebrow">
            Control de acceso
          </p>

          <h2>
            Historial
          </h2>

          <p>
            Registro de entradas,
            salidas y decisiones
            realizadas por SmartPark.
          </p>

        </div>


        <div className="heading-actions">

          <button
            className="secondary-button"
            type="button"
            onClick={loadData}
            disabled={loading}
          >

            <RefreshCw
              size={18}
              className={
                loading
                  ? "spin"
                  : ""
              }
            />

            {loading
              ? "Actualizando..."
              : "Actualizar"}

          </button>

        </div>

      </div>


      {/* ======================================================
          ERROR
          ====================================================== */}

      {error && (

        <div className="alert error">
          {error}
        </div>

      )}


      {/* ======================================================
          RESUMEN
          ====================================================== */}

      <div className="stats-grid">

        <article className="stat-card">

          <div className="stat-icon">

            <History size={23} />

          </div>


          <div>

            <span>
              Eventos registrados
            </span>

            <strong>
              {events.length}
            </strong>

          </div>

        </article>


        <article className="stat-card">

          <div className="stat-icon">

            <ShieldCheck
              size={23}
            />

          </div>


          <div>

            <span>
              Autorizados
            </span>

            <strong>
              {authorizedCount}
            </strong>

          </div>

        </article>


        <article className="stat-card">

          <div className="stat-icon">

            <ShieldX
              size={23}
            />

          </div>


          <div>

            <span>
              Denegados
            </span>

            <strong>
              {deniedCount}
            </strong>

          </div>

        </article>


        <article className="stat-card">

          <div className="stat-icon">

            <LogIn size={23} />

          </div>


          <div>

            <span>
              Entradas
            </span>

            <strong>
              {entryCount}
            </strong>

          </div>

        </article>

      </div>


      {/* ======================================================
          TABLA
          ====================================================== */}

      <article className="panel">

        <div className="panel-header">

          <div>

            <h3>
              Eventos de acceso
            </h3>

            <p>
              Historial obtenido desde
              Amazon RDS mediante el Backend.
            </p>

          </div>

        </div>


        {loading && events.length === 0 ? (

          <div className="empty-state">

            Cargando historial...

          </div>

        ) : events.length === 0 ? (

          <div className="empty-state">

            Todavía no existen
            eventos de acceso registrados.

          </div>

        ) : (

          <div className="table-wrapper">

            <table>

              <thead>

                <tr>

                  <th>
                    Fecha / hora
                  </th>

                  <th>
                    Movimiento
                  </th>

                  <th>
                    Usuario
                  </th>

                  <th>
                    Vehículo
                  </th>

                  <th>
                    Placa detectada
                  </th>

                  <th>
                    Rostro
                  </th>

                  <th>
                    Placa
                  </th>

                  <th>
                    Decisión
                  </th>

                  <th>
                    Motivo
                  </th>

                </tr>

              </thead>


              <tbody>

                {events.map(
                  (event) => {

                    const user =
                      usersById[
                        event.user_id
                      ]


                    const vehicle =
                      vehiclesById[
                        event.vehicle_id
                      ]


                    const decision =
                      getDecisionInfo(
                        event.decision
                      )


                    const eventType =
                      getEventInfo(
                        event.event_type
                      )


                    return (

                      <tr
                        key={
                          event.id
                        }
                      >

                        {/* ================================
                            FECHA
                            ================================ */}

                        <td>

                          <div className="permission-date">

                            <History
                              size={14}
                            />

                            <span>
                              {formatDateTime(
                                event.timestamp
                              )}
                            </span>

                          </div>

                        </td>


                        {/* ================================
                            ENTRY / EXIT
                            ================================ */}

                        <td>

                          <span
                            className={
                              eventType.className
                            }
                          >

                            {eventType.label}

                          </span>

                        </td>


                        {/* ================================
                            USUARIO
                            ================================ */}

                        <td>

                          {user ? (

                            <div className="permission-person">

                              <div className="permission-person-icon">

                                <UserRound
                                  size={15}
                                />

                              </div>


                              <div>

                                <strong>
                                  {user.name}
                                </strong>

                                <span>
                                  {user.institutional_id}
                                </span>

                              </div>

                            </div>

                          ) : (

                            <span>
                              {event.user_id
                                ? `Usuario #${event.user_id}`
                                : "No identificado"}
                            </span>

                          )}

                        </td>


                        {/* ================================
                            VEHÍCULO
                            ================================ */}

                        <td>

                          {vehicle ? (

                            <div className="permission-vehicle">

                              <Car
                                size={16}
                              />

                              <div>

                                <strong>
                                  {vehicle.plate}
                                </strong>

                                <span>
                                  {vehicle.brand}
                                  {" "}
                                  {vehicle.model}
                                </span>

                              </div>

                            </div>

                          ) : (

                            <span>
                              {event.vehicle_id
                                ? `Vehículo #${event.vehicle_id}`
                                : "No identificado"}
                            </span>

                          )}

                        </td>


                        {/* ================================
                            PLACA DETECTADA
                            ================================ */}

                        <td>

                          {event.detected_plate ? (

                            <span className="plate-badge">

                              {event.detected_plate}

                            </span>

                          ) : (

                            "—"

                          )}

                        </td>


                        {/* ================================
                            FACE SCORE
                            ================================ */}

                        <td>

                          <strong>
                            {formatScore(
                              event.face_score
                            )}
                          </strong>

                        </td>


                        {/* ================================
                            PLATE SCORE
                            ================================ */}

                        <td>

                          <strong>
                            {formatScore(
                              event.plate_score
                            )}
                          </strong>

                        </td>


                        {/* ================================
                            DECISIÓN
                            ================================ */}

                        <td>

                          <span
                            className={
                              decision.className
                            }
                          >

                            {decision.label}

                          </span>

                        </td>


                        {/* ================================
                            MOTIVO
                            ================================ */}

                        <td>

                          <span>
                            {event.reason
                              ||
                              "—"}
                          </span>

                        </td>

                      </tr>

                    )
                  }
                )}

              </tbody>

            </table>

          </div>

        )}

      </article>

    </section>
  )
}


export default AccessHistory