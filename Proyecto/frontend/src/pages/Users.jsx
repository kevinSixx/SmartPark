import {
  CheckCircle2,
  CircleAlert,
  RefreshCw,
  ScanFace,
  UserPlus,
  X,
} from "lucide-react"

import {
  useEffect,
  useState,
} from "react"

import {
  Link,
} from "react-router-dom"

import {
  createUser,
  getFaceProfile,
  getUsers,
} from "../api/smartpark"
import TableFilters from "../components/TableFilters"


function Users() {

  const [users, setUsers] = useState([])

  const [faceStatus, setFaceStatus] = useState({})

  const [loading, setLoading] = useState(true)

  const [error, setError] = useState("")

  const [showModal, setShowModal] = useState(false)

  const [name, setName] = useState("")

  const [institutionalId, setInstitutionalId] =
    useState("")

  const [saving, setSaving] = useState(false)

  const [success, setSuccess] = useState("")
  const [query, setQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("")
  const statuses = [...new Set(users.map((user) => user.status).filter(Boolean))]
  const filteredUsers = users.filter((user) =>
    [user.name, user.institutional_id].some((value) =>
      String(value || "").toLocaleLowerCase().includes(query.trim().toLocaleLowerCase())
    ) && (!statusFilter || user.status === statusFilter)
  )


  /* ==========================================================
     CARGAR USUARIOS Y ESTADO FACIAL
     ========================================================== */

  async function loadUsers() {

    try {

      setLoading(true)
      setError("")

      const data = await getUsers()

      const userList = Array.isArray(data) ? data : []
      setUsers(userList)


      /*
       * Mientras consultamos los perfiles,
       * dejamos todos en estado "loading".
       */

      const initialFaceStatus = {}

      userList.forEach(
        (user) => {
          initialFaceStatus[user.id] = "loading"
        }
      )

      setFaceStatus(initialFaceStatus)


      /*
       * Consultamos el perfil facial de
       * cada usuario.
       */

      const results = await Promise.all(
        userList.map(
          async (user) => {

            try {

              const profile =
                await getFaceProfile(user.id)

              return {
                userId: user.id,
                status: profile
                  ? "registered"
                  : "missing",
              }

            } catch (profileError) {

              return {
                userId: user.id,
                status: profileError.status === 404 ? "missing" : "error",
              }

            }

          }
        )
      )


      const nextFaceStatus = {}

      results.forEach(
        (result) => {

          nextFaceStatus[result.userId] =
            result.status

        }
      )

      setFaceStatus(nextFaceStatus)

    } catch (err) {

      setError(err.message)

    } finally {

      setLoading(false)

    }
  }


  useEffect(
    () => {
      loadUsers()
    },
    []
  )


  /* ==========================================================
     MODAL NUEVO USUARIO
     ========================================================== */

  function openModal() {

    setName("")
    setInstitutionalId("")
    setError("")
    setSuccess("")

    setShowModal(true)
  }


  function closeModal() {

    if (saving) {
      return
    }

    setShowModal(false)

    setError("")
    setSuccess("")
  }


  /* ==========================================================
     CREAR USUARIO
     ========================================================== */

  async function handleCreateUser(event) {

    event.preventDefault()
    if (saving) return


    if (
      !name.trim()
      ||
      !institutionalId.trim()
    ) {

      setError(
        "Completa el nombre y el ID institucional."
      )

      return
    }


    try {

      setSaving(true)
      setError("")
      setSuccess("")


      const newUser =
        await createUser({
          name: name.trim(),

          institutional_id:
            institutionalId
              .trim()
              .toUpperCase(),
        })


      setSuccess(
        `Usuario ${newUser?.name || name.trim()} creado correctamente.`
      )


      await loadUsers()


      setTimeout(
        () => {

          setShowModal(false)

          setSuccess("")

        },
        900
      )


    } catch (err) {

      setError(err.message)

    } finally {

      setSaving(false)

    }
  }


  /* ==========================================================
     TEXTO ESTADO FACIAL
     ========================================================== */

  function renderFaceStatus(userId) {

    const status =
      faceStatus[userId]


    if (status === "registered") {

      return (
        <span className="face-status registered">

          <CheckCircle2 size={15} />

          Registrado

        </span>
      )
    }


    if (status === "missing") {

      return (
        <span className="face-status missing">

          <CircleAlert size={15} />

          Sin registrar

        </span>
      )
    }


    if (status === "error") {

      return (
        <span className="face-status unavailable">

          <CircleAlert size={15} />

          No disponible

        </span>
      )
    }


    return (
      <span className="face-status loading">
        Consultando...
      </span>
    )
  }


  /* ==========================================================
     TEXTO BOTÓN FACIAL
     ========================================================== */

  function getFaceActionText(userId) {

    const status =
      faceStatus[userId]


    if (status === "registered") {
      return "Actualizar rostro"
    }


    if (status === "missing") {
      return "Registrar rostro"
    }


    return "Gestionar rostro"
  }


  /* ==========================================================
     INTERFAZ
     ========================================================== */

  return (
    <section>

      <div className="page-heading row-heading">

        <div>

          <p className="eyebrow">
            Administración
          </p>

          <h2>
            Usuarios
          </h2>

          <p>
            Personas registradas en SmartPark.
          </p>

        </div>


        <div className="heading-actions">

          <button
            className="secondary-button"
            type="button"
            onClick={loadUsers}
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


          <button
            className="primary-button"
            type="button"
            onClick={openModal}
          >

            <UserPlus size={18} />

            Nuevo usuario

          </button>

        </div>

      </div>


      {error && !showModal && (

        <div className="alert error">
          {error}
        </div>

      )}


      <article className="panel">

        <div className="panel-header">

          <div>

            <h3>
              Usuarios registrados
            </h3>

            <p>
              {users.length}
              {" "}
              usuarios encontrados.
            </p>

          </div>

        </div>


        <TableFilters query={query} onQueryChange={setQuery} placeholder="Buscar nombre o código"
          count={filteredUsers.length} filters={[{ label: "Estado", value: statusFilter,
            onChange: setStatusFilter, options: statuses.map((value) => ({ value, label: value })) }]} />

        {loading && users.length === 0 ? (

          <div className="empty-state">
            Cargando usuarios...
          </div>

        ) : (

          filteredUsers.length === 0 ? <div className="empty-state">{users.length ? "No hay usuarios que coincidan con los filtros." : "No hay usuarios registrados."}</div> :
          <div className="table-wrapper admin-table-scroll">

            <table>

              <thead>

                <tr>

                  <th>
                    ID
                  </th>

                  <th>
                    Nombre
                  </th>

                  <th>
                    ID institucional
                  </th>

                  <th>
                    Estado
                  </th>

                  <th>
                    Biometría facial
                  </th>

                  <th>
                    Acciones
                  </th>

                </tr>

              </thead>


              <tbody>

                {filteredUsers.map(
                  (user) => (

                    <tr key={user.id}>

                      <td>
                        {user.id != null ? `#${user.id}` : "—"}
                      </td>


                      <td>

                        <strong>
                          {user.name || "Nombre no disponible"}
                        </strong>

                      </td>


                      <td>
                        {user.institutional_id || "No disponible"}
                      </td>


                      <td>

                        <span className="status-badge">
                          {user.status || "No disponible"}
                        </span>

                      </td>


                      <td>

                        {renderFaceStatus(
                          user.id
                        )}

                      </td>


                      <td>

                        {user.id != null ? <Link
                          className="face-action-button"
                          to={
                            `/admin/users/${user.id}/face`
                          }
                        >

                          <ScanFace size={16} />

                          {getFaceActionText(
                            user.id
                          )}

                        </Link> : "No disponible"}

                      </td>

                    </tr>

                  )
                )}

              </tbody>

            </table>

          </div>

        )}

      </article>


      {/* ======================================================
          MODAL NUEVO USUARIO
          ====================================================== */}

      {showModal && (

        <div className="modal-backdrop">

          <div className="modal-card">

            <div className="modal-header">

              <div>

                <p className="eyebrow">
                  SmartPark UCE
                </p>

                <h3>
                  Nuevo usuario
                </h3>

                <p>
                  Registra una nueva persona
                  en el sistema.
                </p>

              </div>


              <button
                className="modal-close"
                type="button"
                onClick={closeModal}
                aria-label="Cerrar"
              >

                <X size={20} />

              </button>

            </div>


            <form
              className="user-form"
              onSubmit={handleCreateUser}
            >

              <label>

                Nombre completo

                <input
                  type="text"
                  placeholder="Ej. Carlos Pérez"
                  value={name}
                  onChange={
                    (event) =>
                      setName(
                        event.target.value
                      )
                  }
                  disabled={saving}
                />

              </label>


              <label>

                ID institucional

                <input
                  type="text"
                  placeholder="Ej. UCE-CP-004"
                  value={institutionalId}
                  onChange={
                    (event) =>
                      setInstitutionalId(
                        event.target.value
                      )
                  }
                  disabled={saving}
                />

              </label>


              {error && (

                <div className="alert error">
                  {error}
                </div>

              )}


              {success && (

                <div className="alert success">
                  {success}
                </div>

              )}


              <div className="modal-actions">

                <button
                  className="secondary-button"
                  type="button"
                  onClick={closeModal}
                  disabled={saving}
                >
                  Cancelar
                </button>


                <button
                  className="primary-button"
                  type="submit"
                  disabled={saving}
                >

                  {saving
                    ? "Guardando..."
                    : "Crear usuario"}

                </button>

              </div>

            </form>

          </div>

        </div>

      )}

    </section>
  )
}


export default Users
