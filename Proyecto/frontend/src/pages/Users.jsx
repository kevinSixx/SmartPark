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


  /* ==========================================================
     CARGAR USUARIOS Y ESTADO FACIAL
     ========================================================== */

  async function loadUsers() {

    try {

      setLoading(true)
      setError("")

      const data = await getUsers()

      setUsers(data)


      /*
       * Mientras consultamos los perfiles,
       * dejamos todos en estado "loading".
       */

      const initialFaceStatus = {}

      data.forEach(
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
        data.map(
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

            } catch {

              return {
                userId: user.id,
                status: "error",
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
        `Usuario ${newUser.name} creado correctamente.`
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


        {loading && users.length === 0 ? (

          <div className="empty-state">
            Cargando usuarios...
          </div>

        ) : (

          <div className="table-wrapper">

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


                      <td>

                        {renderFaceStatus(
                          user.id
                        )}

                      </td>


                      <td>

                        <Link
                          className="face-action-button"
                          to={
                            `/admin/users/${user.id}/face`
                          }
                        >

                          <ScanFace size={16} />

                          {getFaceActionText(
                            user.id
                          )}

                        </Link>

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