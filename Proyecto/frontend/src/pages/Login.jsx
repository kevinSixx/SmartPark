import {
  KeyRound,
  LockKeyhole,
  UserCog,
} from "lucide-react"

import {
  useState,
} from "react"

import {
  useNavigate,
} from "react-router-dom"

import {
  loginStaff,
} from "../api/smartpark"

import {
  setSession,
} from "../utils/session"


function Login() {
  const navigate = useNavigate()

  const [
    username,
    setUsername,
  ] = useState("")

  const [
    password,
    setPassword,
  ] = useState("")

  const [
    loading,
    setLoading,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState("")


  function goToRole(
    role
  ) {

    if (
      role === "GUARD"
    ) {

      navigate(
        "/guard"
      )

      return
    }


    navigate(
      "/admin"
    )
  }


  async function submit(
    event
  ) {

    event.preventDefault()

    setError(
      ""
    )


    if (
      !username.trim()
      ||
      !password
    ) {

      setError(
        "Ingresa usuario y contraseña."
      )

      return
    }


    try {

      setLoading(
        true
      )


      const response = (
        await loginStaff(
          username.trim(),
          password
        )
      )


      const user = (
        response.user
      )


      setSession({
        accessToken:
          response.access_token,

        role:
          user.role,

        name:
          user.full_name,

        username:
          user.username,

        staffId:
          user.id,

        demo:
          false,
      })


      goToRole(
        user.role
      )

    } catch (
      loginError
    ) {

      setError(
        loginError.message
      )

    } finally {

      setLoading(
        false
      )
    }
  }


  return (
    <main className="login-shell login-shell-v2">

      <section className="login-card login-card-v2">

        <div className="login-brand-mark">
          SP
        </div>


        <p className="eyebrow">
          Universidad Central del Ecuador
        </p>


        <h1>
          SmartPark UCE
        </h1>


        <p className="login-intro">
          Plataforma de administración
          y operación de garitas para
          control vehicular inteligente.
        </p>


        <form
          className="smartpark-login-form"
          onSubmit={
            submit
          }
        >

          <label>

            <span>
              Usuario
            </span>

            <div className="login-input-wrap">

              <UserCog
                size={18}
              />

              <input
                value={
                  username
                }
                onChange={
                  (
                    event
                  ) =>
                    setUsername(
                      event.target.value
                    )
                }
                placeholder="Usuario SmartPark"
                autoComplete="username"
              />

            </div>

          </label>


          <label>

            <span>
              Contraseña
            </span>

            <div className="login-input-wrap">

              <LockKeyhole
                size={18}
              />

              <input
                type="password"
                value={
                  password
                }
                onChange={
                  (
                    event
                  ) =>
                    setPassword(
                      event.target.value
                    )
                }
                placeholder="••••••••"
                autoComplete="current-password"
              />

            </div>

          </label>


          {
            error
            &&
            (

              <div className="alert error login-error">
                {error}
              </div>
            )
          }


          <button
            type="submit"
            className="primary-button login-submit-button"
            disabled={
              loading
            }
          >

            <KeyRound
              size={18}
            />

            {
              loading
                ? "Ingresando..."
                : "Iniciar sesión"
            }

          </button>

        </form>


        <div className="login-security-note">
          Acceso restringido a personal
          autorizado de SmartPark.
        </div>

      </section>

    </main>
  )
}


export default Login