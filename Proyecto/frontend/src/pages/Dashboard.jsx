import {
  Activity,
  Database,
  Server,
  Users,
} from "lucide-react"

import {
  useEffect,
  useState,
} from "react"

import {
  getBackendHealth,
  getUsers,
} from "../api/smartpark"


function Dashboard() {

  const [
    users,
    setUsers,
  ] = useState([])

  const [
    backend,
    setBackend,
  ] = useState(null)

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    error,
    setError,
  ] = useState("")


  useEffect(
    () => {

      async function loadDashboard() {

        try {

          setLoading(true)

          const [
            backendData,
            usersData,
          ] = await Promise.all([
            getBackendHealth(),
            getUsers(),
          ])

          setBackend(
            backendData
          )

          setUsers(
            usersData
          )

        } catch (err) {

          setError(
            err.message
          )

        } finally {

          setLoading(false)

        }
      }


      loadDashboard()

    },
    []
  )


  return (
    <section>

      <div className="page-heading">

        <div>
          <p className="eyebrow">
            Resumen general
          </p>

          <h2>
            Dashboard
          </h2>

          <p>
            Estado general del sistema de
            control de acceso vehicular.
          </p>
        </div>

      </div>


      {error && (
        <div className="alert error">
          {error}
        </div>
      )}


      <div className="stats-grid">

        <article className="stat-card">

          <div className="stat-icon">
            <Users size={22} />
          </div>

          <div>
            <span>
              Usuarios registrados
            </span>

            <strong>
              {loading
                ? "..."
                : users.length}
            </strong>
          </div>

        </article>


        <article className="stat-card">

          <div className="stat-icon">
            <Server size={22} />
          </div>

          <div>
            <span>
              Backend
            </span>

            <strong>
              {backend?.status === "ok"
                ? "Operativo"
                : loading
                  ? "..."
                  : "Sin conexión"}
            </strong>
          </div>

        </article>


        <article className="stat-card">

          <div className="stat-icon">
            <Database size={22} />
          </div>

          <div>
            <span>
              Versión API
            </span>

            <strong>
              {backend?.version
                || "..."}
            </strong>
          </div>

        </article>


        <article className="stat-card">

          <div className="stat-icon">
            <Activity size={22} />
          </div>

          <div>
            <span>
              Estado
            </span>

            <strong className="success-text">
              {backend?.status === "ok"
                ? "En línea"
                : "..."}
            </strong>
          </div>

        </article>

      </div>


      <div className="content-grid">

        <article className="panel">

          <div className="panel-header">

            <div>
              <h3>
                Usuarios recientes
              </h3>

              <p>
                Datos obtenidos desde RDS
                mediante el Backend actual de SmartPark.
              </p>
            </div>

          </div>


          {loading ? (

            <div className="empty-state">
              Cargando usuarios...
            </div>

          ) : (

            <div className="table-wrapper">

              <table>

                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Usuario</th>
                    <th>ID institucional</th>
                    <th>Estado</th>
                  </tr>
                </thead>

                <tbody>

                  {users.map(
                    (user) => (

                      <tr key={user.id}>

                        <td>
                          #{user.id}
                        </td>

                        <td>
                          <strong>
                            {user.name}
                          </strong>
                        </td>

                        <td>
                          {user.institutional_id}
                        </td>

                        <td>
                          <span className="status-badge">
                            {user.status}
                          </span>
                        </td>

                      </tr>

                    )
                  )}

                </tbody>

              </table>

            </div>

          )}

        </article>


        <article className="panel system-panel">

          <div className="panel-header">

            <div>
              <h3>
                Infraestructura
              </h3>

              <p>
                Servicios principales.
              </p>
            </div>

          </div>


          <div className="service-list">

            <div className="service-item">
              <div>
                <strong>
                  Backend API
                </strong>

                <span>
                  FastAPI 1.6
                </span>
              </div>

              <span className="online">
                Operativo
              </span>
            </div>


            <div className="service-item">
              <div>
                <strong>
                  Reconocimiento facial
                </strong>

                <span>
                  ArcFace + RetinaFace
                </span>
              </div>

              <span className="online">
                Configurado
              </span>
            </div>


            <div className="service-item">
              <div>
                <strong>
                  Base de datos
                </strong>

                <span>
                  Amazon RDS PostgreSQL
                </span>
              </div>

              <span className="online">
                Conectada
              </span>
            </div>


            <div className="service-item">
              <div>
                <strong>
                  Evidencias
                </strong>

                <span>
                  Amazon S3
                </span>
              </div>

              <span className="online">
                Activo
              </span>
            </div>

          </div>

        </article>

      </div>

    </section>
  )
}


export default Dashboard