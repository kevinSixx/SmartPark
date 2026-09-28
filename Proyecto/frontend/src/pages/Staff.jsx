import {
  BadgeCheck,
  Plus,
  RefreshCw,
  Shield,
  UserCog,
  UsersRound,
} from "lucide-react"

import {
  useEffect,
  useMemo,
  useState,
} from "react"

import {
  createStaffAccount,
  getStaffAccounts,
  updateStaffAccount,
} from "../api/smartpark"


const emptyForm = {
  full_name: "",
  username: "",
  password: "",
  role: "GUARD",
}


function Staff() {
  const [
    accounts,
    setAccounts,
  ] = useState([])

  const [
    form,
    setForm,
  ] = useState(
    emptyForm
  )

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    saving,
    setSaving,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState("")

  const [
    success,
    setSuccess,
  ] = useState("")


  const totals = useMemo(
    () => {

      const active = (
        accounts.filter(
          (
            item
          ) =>
            item.active
        ).length
      )


      const admins = (
        accounts.filter(
          (
            item
          ) =>
            item.role
            ===
            "ADMIN"
        ).length
      )


      const guards = (
        accounts.filter(
          (
            item
          ) =>
            item.role
            ===
            "GUARD"
        ).length
      )


      return {
        active,
        admins,
        guards,
        total:
          accounts.length,
      }
    },
    [
      accounts,
    ]
  )


  async function load() {

    try {

      setLoading(
        true
      )

      setError(
        ""
      )


      const data = (
        await getStaffAccounts()
      )


      setAccounts(
        data
      )

    } catch (
      loadError
    ) {

      setError(
        loadError.message
      )

    } finally {

      setLoading(
        false
      )
    }
  }


  useEffect(
    () => {

      load()

    },
    []
  )


  async function submit(
    event
  ) {

    event.preventDefault()

    setError(
      ""
    )

    setSuccess(
      ""
    )


    if (
      !form.full_name.trim()
      ||
      !form.username.trim()
      ||
      !form.password
    ) {

      setError(
        "Completa nombre, usuario y contraseña."
      )

      return
    }


    try {

      setSaving(
        true
      )


      await createStaffAccount({

        full_name:
          form.full_name.trim(),

        username:
          form.username
            .trim()
            .toLowerCase(),

        password:
          form.password,

        role:
          form.role,

        active:
          true,
      })


      setForm(
        emptyForm
      )


      setSuccess(
        "Cuenta de personal creada correctamente."
      )


      await load()

    } catch (
      saveError
    ) {

      setError(
        saveError.message
      )

    } finally {

      setSaving(
        false
      )
    }
  }


  async function toggleActive(
    account
  ) {

    try {

      setError(
        ""
      )

      setSuccess(
        ""
      )


      await updateStaffAccount(
        account.id,
        {
          active:
            !account.active,
        }
      )


      setSuccess(
        account.active
          ? "Cuenta desactivada."
          : "Cuenta activada."
      )


      await load()

    } catch (
      toggleError
    ) {

      setError(
        toggleError.message
      )
    }
  }


  return (
    <section>

      <div className="page-heading staff-page-heading">

        <div>

          <p className="eyebrow">
            Administración
          </p>


          <h2>
            Guardias y personal
          </h2>


          <p>
            Cuentas administrativas y
            operativas almacenadas en
            Amazon RDS.
          </p>

        </div>


        <button
          type="button"
          className="secondary-button"
          onClick={
            load
          }
        >

          <RefreshCw
            size={18}
          />

          Actualizar

        </button>

      </div>


      <div className="stats-grid staff-stats-grid">

        <article className="stat-card">

          <div className="stat-icon">

            <UsersRound
              size={22}
            />

          </div>


          <div>

            <span>
              Total
            </span>

            <strong>
              {totals.total}
            </strong>

          </div>

        </article>


        <article className="stat-card">

          <div className="stat-icon">

            <BadgeCheck
              size={22}
            />

          </div>


          <div>

            <span>
              Activos
            </span>

            <strong>
              {totals.active}
            </strong>

          </div>

        </article>


        <article className="stat-card">

          <div className="stat-icon">

            <UserCog
              size={22}
            />

          </div>


          <div>

            <span>
              Administradores
            </span>

            <strong>
              {totals.admins}
            </strong>

          </div>

        </article>


        <article className="stat-card">

          <div className="stat-icon">

            <Shield
              size={22}
            />

          </div>


          <div>

            <span>
              Guardias
            </span>

            <strong>
              {totals.guards}
            </strong>

          </div>

        </article>

      </div>


      {
        (
          error
          ||
          success
        )
        &&
        (

          <div className="staff-message-stack">

            {
              error
              &&
              (

                <div className="alert error">
                  {error}
                </div>
              )
            }


            {
              success
              &&
              (

                <div className="alert success">
                  {success}
                </div>
              )
            }

          </div>
        )
      }


      <div className="staff-workspace-grid">

        <article className="panel staff-create-panel">

          <div className="panel-header">

            <div>

              <h3>
                Nueva cuenta
              </h3>


              <p>
                Registra un administrador
                o guardia para SmartPark.
              </p>

            </div>


            <Plus
              size={20}
            />

          </div>


          <form
            className="staff-form"
            onSubmit={
              submit
            }
          >

            <label>

              <span>
                Nombre completo
              </span>


              <input
                value={
                  form.full_name
                }
                onChange={
                  (
                    event
                  ) =>
                    setForm({
                      ...form,

                      full_name:
                        event.target.value,
                    })
                }
                placeholder="Juan Pérez"
              />

            </label>


            <label>

              <span>
                Usuario
              </span>


              <input
                value={
                  form.username
                }
                onChange={
                  (
                    event
                  ) =>
                    setForm({
                      ...form,

                      username:
                        event.target.value,
                    })
                }
                placeholder="jperez"
                autoComplete="off"
              />

            </label>


            <label>

              <span>
                Contraseña inicial
              </span>


              <input
                type="password"
                value={
                  form.password
                }
                onChange={
                  (
                    event
                  ) =>
                    setForm({
                      ...form,

                      password:
                        event.target.value,
                    })
                }
                placeholder="Mínimo 6 caracteres"
                autoComplete="new-password"
              />

            </label>


            <label>

              <span>
                Rol
              </span>


              <select
                value={
                  form.role
                }
                onChange={
                  (
                    event
                  ) =>
                    setForm({
                      ...form,

                      role:
                        event.target.value,
                    })
                }
              >

                <option value="GUARD">
                  GUARD
                </option>


                <option value="ADMIN">
                  ADMIN
                </option>

              </select>

            </label>


            <button
              type="submit"
              className="primary-button"
              disabled={
                saving
              }
            >

              <Plus
                size={18}
              />

              {
                saving
                  ? "Creando..."
                  : "Crear cuenta"
              }

            </button>

          </form>

        </article>


        <article className="panel staff-list-panel">

          <div className="panel-header">

            <div>

              <h3>
                Personal registrado
              </h3>


              <p>
                Usuarios autorizados para
                operar SmartPark.
              </p>

            </div>

          </div>


          {
            loading
              ? (

                <div className="empty-state">
                  Consultando personal...
                </div>

              )
              : accounts.length
                ===
                0
                ? (

                  <div className="empty-state">
                    No existen cuentas registradas.
                  </div>

                )
                : (

                  <div className="staff-account-list">

                    {
                      accounts.map(
                        (
                          account
                        ) => (

                          <div
                            className="staff-account-row"
                            key={
                              account.id
                            }
                          >

                            <div className="staff-account-main">

                              <span
                                className={
                                  `staff-role-badge ${account.role.toLowerCase()}`
                                }
                              >

                                {
                                  account.role
                                }

                              </span>


                              <div>

                                <strong>
                                  {
                                    account.full_name
                                  }
                                </strong>


                                <span>
                                  @
                                  {
                                    account.username
                                  }
                                </span>

                              </div>

                            </div>


                            <div className="staff-account-actions">

                              <span
                                className={
                                  `status-badge ${
                                    account.active
                                      ? "active"
                                      : "inactive"
                                  }`
                                }
                              >

                                {
                                  account.active
                                    ? "ACTIVO"
                                    : "INACTIVO"
                                }

                              </span>


                              <button
                                type="button"
                                className="secondary-button compact-button"
                                onClick={
                                  () =>
                                    toggleActive(
                                      account
                                    )
                                }
                              >

                                {
                                  account.active
                                    ? "Desactivar"
                                    : "Activar"
                                }

                              </button>

                            </div>

                          </div>
                        )
                      )
                    }

                  </div>
                )
          }

        </article>

      </div>

    </section>
  )
}


export default Staff