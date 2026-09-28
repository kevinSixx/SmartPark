import {
  CalendarDays,
  Car,
  CheckCircle2,
  Clock3,
  Plus,
  RefreshCw,
  ShieldCheck,
  UserRound,
  X,
} from "lucide-react"

import {
  useEffect,
  useMemo,
  useState,
} from "react"

import {
  createPermission,
  getPermissions,
  getUsers,
  getVehicles,
} from "../api/smartpark"


function Permissions() {

  const [permissions, setPermissions] =
    useState([])

  const [users, setUsers] =
    useState([])

  const [vehicles, setVehicles] =
    useState([])

  const [loading, setLoading] =
    useState(true)

  const [showModal, setShowModal] =
    useState(false)

  const [saving, setSaving] =
    useState(false)

  const [error, setError] =
    useState("")

  const [success, setSuccess] =
    useState("")


  /* ==========================================================
     FORMULARIO
     ========================================================== */

  const [userId, setUserId] =
    useState("")

  const [vehicleId, setVehicleId] =
    useState("")

  const [validFrom, setValidFrom] =
    useState("")

  const [validTo, setValidTo] =
    useState("")

  const [active, setActive] =
    useState(true)


  /* ==========================================================
     MAPAS
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


  const vehiclesById =
    useMemo(
      () => {

        const map = {}

        vehicles.forEach(
          (vehicle) => {

            map[vehicle.id] = vehicle

          }
        )

        return map

      },
      [vehicles]
    )


  /* ==========================================================
     VEHÍCULOS DEL USUARIO SELECCIONADO
     ========================================================== */

  const userVehicles =
    useMemo(
      () => {

        if (!userId) {
          return []
        }


        return vehicles.filter(
          (vehicle) =>
            Number(vehicle.user_id)
            ===
            Number(userId)
        )

      },
      [
        vehicles,
        userId,
      ]
    )


  /* ==========================================================
     CARGAR DATOS
     ========================================================== */

  async function loadData() {

    try {

      setLoading(true)
      setError("")


      const [
        permissionsData,
        usersData,
        vehiclesData,
      ] = await Promise.all([
        getPermissions(),
        getUsers(),
        getVehicles(),
      ])


      setPermissions(
        permissionsData
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
     DATETIME LOCAL
     ========================================================== */

  function toDateTimeLocal(
    date
  ) {

    const pad =
      (value) =>
        String(value)
          .padStart(2, "0")


    return (
      `${date.getFullYear()}-`
      +
      `${pad(date.getMonth() + 1)}-`
      +
      `${pad(date.getDate())}T`
      +
      `${pad(date.getHours())}:`
      +
      `${pad(date.getMinutes())}`
    )
  }


  /* ==========================================================
     ABRIR MODAL
     ========================================================== */

  function openModal() {

    const now =
      new Date()

    const future =
      new Date()

    future.setDate(
      future.getDate() + 30
    )


    setUserId("")
    setVehicleId("")

    setValidFrom(
      toDateTimeLocal(now)
    )

    setValidTo(
      toDateTimeLocal(future)
    )

    setActive(true)

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
     CAMBIAR USUARIO
     ========================================================== */

  function handleUserChange(
    event
  ) {

    setUserId(
      event.target.value
    )

    /*
     * Al cambiar de usuario,
     * limpiamos el vehículo anterior.
     */

    setVehicleId("")
  }


  /* ==========================================================
     CREAR PERMISO
     ========================================================== */

  async function handleCreatePermission(
    event
  ) {

    event.preventDefault()


    if (!userId) {

      setError(
        "Selecciona un usuario."
      )

      return
    }


    if (!vehicleId) {

      setError(
        "Selecciona un vehículo."
      )

      return
    }


    if (!validFrom) {

      setError(
        "Selecciona la fecha de inicio."
      )

      return
    }


    if (!validTo) {

      setError(
        "Selecciona la fecha de finalización."
      )

      return
    }


    const startDate =
      new Date(validFrom)

    const endDate =
      new Date(validTo)


    if (
      Number.isNaN(
        startDate.getTime()
      )
      ||
      Number.isNaN(
        endDate.getTime()
      )
    ) {

      setError(
        "Las fechas ingresadas no son válidas."
      )

      return
    }


    if (
      endDate <= startDate
    ) {

      setError(
        "La fecha final debe ser posterior a la fecha inicial."
      )

      return
    }


    const selectedVehicle =
      vehicles.find(
        (vehicle) =>
          Number(vehicle.id)
          ===
          Number(vehicleId)
      )


    if (
      !selectedVehicle
      ||
      Number(
        selectedVehicle.user_id
      )
      !==
      Number(userId)
    ) {

      setError(
        "El vehículo seleccionado no pertenece al usuario."
      )

      return
    }


    try {

      setSaving(true)
      setError("")
      setSuccess("")


      await createPermission({
        valid_from:
          startDate.toISOString(),

        valid_to:
          endDate.toISOString(),

        user_id:
          Number(userId),

        vehicle_id:
          Number(vehicleId),

        active:
          active,
      })


      setSuccess(
        "Permiso registrado correctamente."
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

      setError(
        err.message
      )

    } finally {

      setSaving(false)

    }
  }


  /* ==========================================================
     FORMATO DE FECHAS
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
          "short",
      }
    ).format(date)
  }


  /* ==========================================================
     ESTADO TEMPORAL DEL PERMISO
     ========================================================== */

  function getPermissionState(
    permission
  ) {

    if (!permission.active) {

      return {
        label:
          "INACTIVO",

        className:
          "inactive",
      }
    }


    const now =
      new Date()

    const start =
      new Date(
        permission.valid_from
      )

    const end =
      new Date(
        permission.valid_to
      )


    if (now < start) {

      return {
        label:
          "PROGRAMADO",

        className:
          "scheduled",
      }
    }


    if (now > end) {

      return {
        label:
          "EXPIRADO",

        className:
          "expired",
      }
    }


    return {
      label:
        "VIGENTE",

      className:
        "valid",
    }
  }


  /* ==========================================================
     CONTADORES
     ========================================================== */

  const validPermissions =
    permissions.filter(
      (permission) =>
        getPermissionState(
          permission
        ).label
        ===
        "VIGENTE"
    ).length


  const activePermissions =
    permissions.filter(
      (permission) =>
        permission.active
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
            Permisos
          </h2>

          <p>
            Autoriza usuarios y vehículos
            para ingresar a SmartPark.
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

            Nuevo permiso

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

      <div className="permission-summary-grid">

        <article className="permission-summary-card">

          <div className="permission-summary-icon">

            <ShieldCheck size={23} />

          </div>


          <div>

            <span>
              Permisos registrados
            </span>

            <strong>
              {permissions.length}
            </strong>

          </div>

        </article>


        <article className="permission-summary-card">

          <div className="permission-summary-icon">

            <CheckCircle2 size={23} />

          </div>


          <div>

            <span>
              Permisos vigentes
            </span>

            <strong>
              {validPermissions}
            </strong>

          </div>

        </article>


        <article className="permission-summary-card">

          <div className="permission-summary-icon">

            <Clock3 size={23} />

          </div>


          <div>

            <span>
              Permisos activos
            </span>

            <strong>
              {activePermissions}
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
              Permisos registrados
            </h3>

            <p>
              Autorizaciones almacenadas
              en Amazon RDS.
            </p>

          </div>

        </div>


        {loading && permissions.length === 0 ? (

          <div className="empty-state">
            Cargando permisos...
          </div>

        ) : permissions.length === 0 ? (

          <div className="permission-empty-state">

            <div className="permission-empty-icon">

              <ShieldCheck size={30} />

            </div>


            <strong>
              No hay permisos registrados
            </strong>


            <p>
              Crea un permiso para autorizar
              un usuario y su vehículo.
            </p>


            <button
              className="primary-button"
              type="button"
              onClick={openModal}
            >

              <Plus size={18} />

              Nuevo permiso

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
                    Usuario
                  </th>

                  <th>
                    Vehículo
                  </th>

                  <th>
                    Desde
                  </th>

                  <th>
                    Hasta
                  </th>

                  <th>
                    Estado
                  </th>

                </tr>

              </thead>


              <tbody>

                {permissions.map(
                  (permission) => {

                    const user =
                      usersById[
                        permission.user_id
                      ]


                    const vehicle =
                      vehiclesById[
                        permission.vehicle_id
                      ]


                    const state =
                      getPermissionState(
                        permission
                      )


                    return (

                      <tr
                        key={
                          permission.id
                        }
                      >

                        <td>
                          #{permission.id}
                        </td>


                        <td>

                          <div className="permission-person">

                            <div className="permission-person-icon">

                              <UserRound
                                size={15}
                              />

                            </div>


                            <div>

                              <strong>
                                {user?.name
                                  ||
                                  `Usuario #${permission.user_id}`}
                              </strong>

                              <span>
                                {user?.institutional_id
                                  ||
                                  ""}
                              </span>

                            </div>

                          </div>

                        </td>


                        <td>

                          <div className="permission-vehicle">

                            <Car
                              size={16}
                            />

                            <div>

                              <strong>
                                {vehicle?.plate
                                  ||
                                  `Vehículo #${permission.vehicle_id}`}
                              </strong>

                              <span>
                                {vehicle
                                  ? `${vehicle.brand} ${vehicle.model}`
                                  : ""}
                              </span>

                            </div>

                          </div>

                        </td>


                        <td>

                          <div className="permission-date">

                            <CalendarDays
                              size={14}
                            />

                            <span>
                              {formatDateTime(
                                permission.valid_from
                              )}
                            </span>

                          </div>

                        </td>


                        <td>

                          <div className="permission-date">

                            <CalendarDays
                              size={14}
                            />

                            <span>
                              {formatDateTime(
                                permission.valid_to
                              )}
                            </span>

                          </div>

                        </td>


                        <td>

                          <span
                            className={
                              `permission-state ${state.className}`
                            }
                          >

                            {state.label}

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
          MODAL
          ====================================================== */}

      {showModal && (

        <div className="modal-backdrop">

          <div className="modal-card permission-modal-card">

            <div className="modal-header">

              <div>

                <p className="eyebrow">
                  SmartPark UCE
                </p>

                <h3>
                  Nuevo permiso
                </h3>

                <p>
                  Autoriza un usuario y
                  su vehículo durante un
                  período determinado.
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
              className="user-form permission-form"
              onSubmit={
                handleCreatePermission
              }
            >

              {/* ==============================================
                  USUARIO
                  ============================================== */}

              <label>

                Usuario

                <select
                  value={userId}
                  onChange={
                    handleUserChange
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
                  VEHÍCULO
                  ============================================== */}

              <label>

                Vehículo

                <select
                  value={vehicleId}
                  onChange={
                    (event) =>
                      setVehicleId(
                        event.target.value
                      )
                  }
                  disabled={
                    saving
                    ||
                    !userId
                  }
                >

                  <option value="">

                    {!userId
                      ? "Primero selecciona un usuario"
                      : userVehicles.length === 0
                        ? "El usuario no tiene vehículos"
                        : "Selecciona un vehículo"}

                  </option>


                  {userVehicles.map(
                    (vehicle) => (

                      <option
                        key={vehicle.id}
                        value={vehicle.id}
                      >

                        {vehicle.plate}
                        {" · "}
                        {vehicle.brand}
                        {" "}
                        {vehicle.model}

                      </option>

                    )
                  )}

                </select>

              </label>


              {/* ==============================================
                  FECHAS
                  ============================================== */}

              <div className="permission-form-grid">

                <label>

                  Válido desde

                  <input
                    type="datetime-local"
                    value={validFrom}
                    onChange={
                      (event) =>
                        setValidFrom(
                          event.target.value
                        )
                    }
                    disabled={saving}
                  />

                </label>


                <label>

                  Válido hasta

                  <input
                    type="datetime-local"
                    value={validTo}
                    onChange={
                      (event) =>
                        setValidTo(
                          event.target.value
                        )
                    }
                    disabled={saving}
                  />

                </label>

              </div>


              {/* ==============================================
                  ACTIVE
                  ============================================== */}

              <label className="permission-toggle">

                <div>

                  <strong>
                    Permiso activo
                  </strong>

                  <span>
                    El sistema utilizará
                    este permiso para la
                    autorización de acceso.
                  </span>

                </div>


                <input
                  type="checkbox"
                  checked={active}
                  onChange={
                    (event) =>
                      setActive(
                        event.target.checked
                      )
                  }
                  disabled={saving}
                />

              </label>


              {/* ==============================================
                  INFO
                  ============================================== */}

              <div className="permission-info">

                <div className="permission-info-icon">

                  <ShieldCheck
                    size={19}
                  />

                </div>


                <div>

                  <strong>
                    Autorización SmartPark
                  </strong>

                  <span>
                    Para permitir el acceso,
                    el rostro, la placa,
                    el vehículo y el permiso
                    deben coincidir.
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

                  <ShieldCheck
                    size={18}
                  />

                  {saving
                    ? "Registrando..."
                    : "Registrar permiso"}

                </button>

              </div>

            </form>

          </div>

        </div>

      )}

    </section>
  )
}


export default Permissions