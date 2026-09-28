import {
  Bell,
  CircleUserRound,
  ShieldCheck,
} from "lucide-react"

import {
  getSession,
} from "../utils/session"


function Header({ role = "ADMIN" }) {
  const session = getSession()
  const isGuard = role === "GUARD"

  return (
    <header className={
      `topbar ${isGuard ? "guard-topbar" : ""}`
    }>
      <div>
        <p className="topbar-eyebrow">
          {isGuard
            ? "Operación de garita"
            : "Sistema inteligente de acceso"}
        </p>

        <h1>
          {isGuard
            ? "SmartPark · Garita 01"
            : "SmartPark UCE"}
        </h1>
      </div>

      <div className="topbar-actions">
        <button
          className="icon-button"
          type="button"
          aria-label="Notificaciones"
        >
          <Bell size={20} />
        </button>

        <div className="admin-profile">
          {isGuard
            ? <ShieldCheck size={30} />
            : <CircleUserRound size={30} />}

          <div>
            <strong>
              {session?.name || (isGuard ? "Guardia" : "Administrador")}
            </strong>

            <span>
              {isGuard ? "Garita 01" : "SmartPark"}
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
