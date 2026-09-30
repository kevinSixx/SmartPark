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
import TableFilters from "../components/TableFilters"


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
  const [query, setQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("")


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

      setVehicles(Array.isArray(vehicleData) ? vehicleData : [])
      setUsers(Array.isArray(userData) ? userData : [])

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
        /[\s-]/g,
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
    if (saving) return


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

    const normalizedPlate = normalizePlate(plate)
    if (!/^[A-Z]{3}[0-9]{3,4}$/.test(normalizedPlate)) {
      setError("Ingresa una placa válida, por ejemplo PAA-1234.")
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
        `Vehículo ${newVehicle?.plate || normalizedPlate} registrado correctamente.`
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
  const statuses = [...new Set(vehicles.map((vehicle) => vehicle.status).filter(Boolean))]
  const filteredVehicles = vehicles.filter((vehicle) => {
    const owner = usersById[vehicle.user_id]
    return [vehicle.plate, owner?.name, vehicle.brand, vehicle.model]
      .some((value) => String(value || "").toLocaleLowerCase().includes(query.trim().toLocaleLowerCase()))
      && (!statusFilter || vehicle.status === statusFilter)
  })


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


        <TableFilters query={query} onQueryChange={setQuery} placeholder="Buscar placa, propietario, marca o modelo"
          count={filteredVehicles.length} filters={[{ label: "Estado", value: statusFilter,
            onChange: setStatusFilter, options: statuses.map((value) => ({ value, label: value })) }]} />

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

          filteredVehicles.length === 0 ? <div className="empty-state">No hay vehículos que coincidan con los filtros.</div> :
          <div className="table-wrapper admin-table-scroll">

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

                {filteredVehicles.map(
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
                          {vehicle.id != null ? `#${vehicle.id}` : "—"}
                        </td>


                        <td>

                          <span className="plate-badge">
                            {vehicle.plate || "Placa no disponible"}
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
                                  "No identificado"}
                              </strong>

                              <span>
                                {owner?.institutional_id
                                  ||
                                  "ID institucional no disponible"}
                              </span>

                            </div>

                          </div>

                        </td>


                        <td>
                          {vehicle.brand || "No disponible"}
                        </td>


                        <td>
                          {vehicle.model || "No disponible"}
                        </td>


                        <td>

                          <span className="vehicle-color">

                            <span className="vehicle-color-dot" />

                            {vehicle.color || "No disponible"}

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

                            {vehicle.status || "No disponible"}

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
