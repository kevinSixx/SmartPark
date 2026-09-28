import {
  Car,
  Plus,
  RefreshCw,
  UserRound,
  X,
} from "lucide-react"

import {
  useEffect,
  useMemo,
  useState,
} from "react"

import {
  createVehicle,
  getUsers,
  getVehicles,
} from "../api/smartpark"


function Vehicles() {

  const [vehicles, setVehicles] =
    useState([])

  const [users, setUsers] =
    useState([])

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState("")

  const [showModal, setShowModal] =
    useState(false)

  const [saving, setSaving] =
    useState(false)

  const [success, setSuccess] =
    useState("")


  /* ==========================================================
     FORMULARIO
     ========================================================== */

  const [userId, setUserId] =
    useState("")

  const [plate, setPlate] =
    useState("")

  const [brand, setBrand] =
    useState("")

  const [model, setModel] =
    useState("")

  const [color, setColor] =
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
            map[user.id] = user
          }
        )

        return map
      },
      [users]
    )


  /* ==========================================================
     CARGAR DATOS
     ========================================================== */

  async function loadData() {

    try {

      setLoading(true)
      setError("")

      const [
        vehicleData,
        userData,
      ] = await Promise.all([
        getVehicles(),
        getUsers(),
      ])

      setVehicles(vehicleData)
      setUsers(userData)

    } catch (err) {

      setError(err.message)

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
     ABRIR MODAL
     ========================================================== */

  function openModal() {

    setUserId("")
    setPlate("")
    setBrand("")
    setModel("")
    setColor("")

    setError("")
    setSuccess("")

    setShowModal(true)
  }


  /* ==========================================================
     CERRAR MODAL
     ========================================================== */

  function closeModal() {

    if (saving) {
      return
    }

    setShowModal(false)

    setError("")
    setSuccess("")
  }


  /* ==========================================================
     NORMALIZAR PLACA
     ========================================================== */

  function normalizePlate(value) {

    return value
      .replace(
        /[^a-zA-Z0-9]/g,
        ""
      )
      .toUpperCase()
  }


  /* ==========================================================
     CREAR VEHÍCULO
     ========================================================== */

  async function handleCreateVehicle(
    event
  ) {

    event.preventDefault()


    if (!userId) {

      setError(
        "Selecciona el propietario del vehículo."
      )

      return
    }


    if (!plate.trim()) {

      setError(
        "Ingresa la placa del vehículo."
      )

      return
    }


    if (!brand.trim()) {

      setError(
        "Ingresa la marca del vehículo."
      )

      return
    }


    if (!model.trim()) {

      setError(
        "Ingresa el modelo del vehículo."
      )

      return
    }


    if (!color.trim()) {

      setError(
        "Ingresa el color del vehículo."
      )

      return
    }


    try {

      setSaving(true)
      setError("")
      setSuccess("")


      const normalizedPlate =
        normalizePlate(plate)


      const newVehicle =
        await createVehicle({
          user_id:
            Number(userId),

          plate:
            normalizedPlate,

          brand:
            brand.trim(),

          model:
            model.trim(),

          color:
            color.trim(),

          status:
            "ACTIVE",
        })


      setSuccess(
        `Vehículo ${newVehicle.plate} registrado correctamente.`
      )


      await loadData()


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
     CONTADORES
     ========================================================== */

  const activeVehicles =
    vehicles.filter(
      (vehicle) =>
        vehicle.status === "ACTIVE"
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
            Administración
          </p>

          <h2>
            Vehículos
          </h2>

          <p>
            Vehículos registrados para
            el control de acceso de SmartPark.
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


          <button
            className="primary-button"
            type="button"
            onClick={openModal}
          >

            <Plus size={18} />

            Nuevo vehículo

          </button>

        </div>

      </div>


      {/* ======================================================
          ERROR
          ====================================================== */}

      {error && !showModal && (

        <div className="alert error">
          {error}
        </div>

      )}


      {/* ======================================================
          RESUMEN
          ====================================================== */}

      <div className="vehicle-summary-grid">

        <article className="vehicle-summary-card">

          <div className="vehicle-summary-icon">

            <Car size={23} />

          </div>


          <div>

            <span>
              Vehículos registrados
            </span>

            <strong>
              {vehicles.length}
            </strong>

          </div>

        </article>


        <article className="vehicle-summary-card">

          <div className="vehicle-summary-icon">

            <Car size={23} />

          </div>


          <div>

            <span>
              Vehículos activos
            </span>

            <strong>
              {activeVehicles}
            </strong>

          </div>

        </article>


        <article className="vehicle-summary-card">

          <div className="vehicle-summary-icon">

            <UserRound size={23} />

          </div>


          <div>

            <span>
              Usuarios disponibles
            </span>

            <strong>
              {users.length}
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
              Vehículos registrados
            </h3>

            <p>
              Datos almacenados en
              Amazon RDS mediante el Backend.
            </p>

          </div>

        </div>


        {loading && vehicles.length === 0 ? (

          <div className="empty-state">
            Cargando vehículos...
          </div>

        ) : vehicles.length === 0 ? (

          <div className="vehicle-empty-state">

            <div className="vehicle-empty-icon">

              <Car size={30} />

            </div>

            <strong>
              No hay vehículos registrados
            </strong>

            <p>
              Registra el primer vehículo
              para comenzar a utilizar el
              control de acceso.
            </p>

            <button
              className="primary-button"
              type="button"
              onClick={openModal}
            >

              <Plus size={18} />

              Nuevo vehículo

            </button>

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
                    Placa
                  </th>

                  <th>
                    Propietario
                  </th>

                  <th>
                    Marca
                  </th>

                  <th>
                    Modelo
                  </th>

                  <th>
                    Color
                  </th>

                  <th>
                    Estado
                  </th>

                </tr>

              </thead>


              <tbody>

                {vehicles.map(
                  (vehicle) => {

                    const owner =
                      usersById[
                        vehicle.user_id
                      ]

                    return (

                      <tr
                        key={
                          vehicle.id
                        }
                      >

                        <td>
                          #{vehicle.id}
                        </td>


                        <td>

                          <span className="plate-badge">
                            {vehicle.plate}
                          </span>

                        </td>


                        <td>

                          <div className="vehicle-owner">

                            <div className="vehicle-owner-icon">

                              <UserRound
                                size={15}
                              />

                            </div>


                            <div>

                              <strong>
                                {owner?.name
                                  ||
                                  `Usuario #${vehicle.user_id}`}
                              </strong>

                              <span>
                                {owner?.institutional_id
                                  ||
                                  ""}
                              </span>

                            </div>

                          </div>

                        </td>


                        <td>
                          {vehicle.brand}
                        </td>


                        <td>
                          {vehicle.model}
                        </td>


                        <td>

                          <span className="vehicle-color">

                            <span className="vehicle-color-dot" />

                            {vehicle.color}

                          </span>

                        </td>


                        <td>

                          <span
                            className={
                              vehicle.status
                              ===
                              "ACTIVE"
                                ? "status-badge"
                                : "status-badge inactive"
                            }
                          >

                            {vehicle.status}

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


      {/* ======================================================
          MODAL NUEVO VEHÍCULO
          ====================================================== */}

      {showModal && (

        <div className="modal-backdrop">

          <div className="modal-card vehicle-modal-card">

            <div className="modal-header">

              <div>

                <p className="eyebrow">
                  SmartPark UCE
                </p>

                <h3>
                  Nuevo vehículo
                </h3>

                <p>
                  Registra un vehículo y
                  asígnalo a un usuario.
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
              className="user-form vehicle-form"
              onSubmit={
                handleCreateVehicle
              }
            >

              {/* ==============================================
                  PROPIETARIO
                  ============================================== */}

              <label>

                Propietario

                <select
                  value={userId}
                  onChange={
                    (event) =>
                      setUserId(
                        event.target.value
                      )
                  }
                  disabled={saving}
                >

                  <option value="">
                    Selecciona un usuario
                  </option>


                  {users.map(
                    (user) => (

                      <option
                        key={user.id}
                        value={user.id}
                      >

                        {user.name}
                        {" · "}
                        {user.institutional_id}

                      </option>

                    )
                  )}

                </select>

              </label>


              {/* ==============================================
                  PLACA
                  ============================================== */}

              <label>

                Placa

                <input
                  type="text"
                  placeholder="Ej. TDH398"
                  value={plate}
                  maxLength={10}
                  onChange={
                    (event) =>
                      setPlate(
                        normalizePlate(
                          event.target.value
                        )
                      )
                  }
                  disabled={saving}
                />

              </label>


              <div className="vehicle-form-grid">

                {/* ============================================
                    MARCA
                    ============================================ */}

                <label>

                  Marca

                  <input
                    type="text"
                    placeholder="Ej. Chevrolet"
                    value={brand}
                    onChange={
                      (event) =>
                        setBrand(
                          event.target.value
                        )
                    }
                    disabled={saving}
                  />

                </label>


                {/* ============================================
                    MODELO
                    ============================================ */}

                <label>

                  Modelo

                  <input
                    type="text"
                    placeholder="Ej. Sail"
                    value={model}
                    onChange={
                      (event) =>
                        setModel(
                          event.target.value
                        )
                    }
                    disabled={saving}
                  />

                </label>

              </div>


              {/* ==============================================
                  COLOR
                  ============================================== */}

              <label>

                Color

                <input
                  type="text"
                  placeholder="Ej. Blanco"
                  value={color}
                  onChange={
                    (event) =>
                      setColor(
                        event.target.value
                      )
                  }
                  disabled={saving}
                />

              </label>


              <div className="vehicle-active-info">

                <div className="vehicle-active-icon">

                  <Car size={19} />

                </div>


                <div>

                  <strong>
                    Estado inicial: ACTIVE
                  </strong>

                  <span>
                    El vehículo quedará activo
                    después del registro.
                  </span>

                </div>

              </div>


              {/* ==============================================
                  MENSAJES
                  ============================================== */}

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


              {/* ==============================================
                  BOTONES
                  ============================================== */}

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

                  <Car size={18} />

                  {saving
                    ? "Registrando..."
                    : "Registrar vehículo"}

                </button>

              </div>

            </form>

          </div>

        </div>

      )}

    </section>
  )
}


export default Vehicles