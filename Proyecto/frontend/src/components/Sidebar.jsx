import {
  CarFront,
  DoorOpen,
  History,
  LayoutDashboard,
  LogOut,
  ScanFace,
  ShieldCheck,
  UserCog,
  Users,
} from "lucide-react"

import {
  NavLink,
  useNavigate,
} from "react-router-dom"

import {
  clearSession,
} from "../utils/session"


const adminMenu = [
  {
    to: "/admin",
    label: "Dashboard",
    icon: LayoutDashboard,
  },
  {
    to: "/admin/users",
    label: "Usuarios",
    icon: Users,
  },
  {
    to: "/admin/vehicles",
    label: "Vehículos",
    icon: CarFront,
  },
  {
    to: "/admin/permissions",
    label: "Permisos",
    icon: ShieldCheck,
  },
  {
    to: "/admin/history",
    label: "Historial",
    icon: History,
  },
  {
    to: "/admin/access-test",
    label: "Prueba de acceso",
    icon: ScanFace,
  },
  {
    to: "/admin/staff",
    label: "Guardias",
    icon: UserCog,
  },
]

const guardMenu = [
  {
    to: "/guard",
    label: "Garita 01",
    icon: DoorOpen,
  },
  {
    to: "/guard/history",
    label: "Eventos",
    icon: History,
  },
]


function Sidebar({ role = "ADMIN" }) {
  const navigate = useNavigate()
  const isGuard = role === "GUARD"
  const menu = isGuard
    ? guardMenu
    : adminMenu

  function logout() {
    clearSession()
    navigate("/login")
  }

  return (
    <aside className={
      `sidebar ${isGuard ? "guard-sidebar" : ""}`
    }>
      <div className="sidebar-brand">
        <div className="brand-icon">
          SP
        </div>

        <div>
          <strong>SmartPark</strong>
          <span>
            {isGuard
              ? "Centro de control"
              : "Universidad Central"}
          </span>
        </div>
      </div>

      <div className="sidebar-role-label">
        {isGuard ? "GUARDIA" : "ADMINISTRACIÓN"}
      </div>

      <nav className="sidebar-nav">
        {menu.map(
          ({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={
                to === "/admin" ||
                to === "/guard"
              }
              className={
                ({ isActive }) =>
                  isActive
                    ? "nav-item active"
                    : "nav-item"
              }
            >
              <Icon size={20} />
              <span>{label}</span>
            </NavLink>
          )
        )}
      </nav>

      <div className="sidebar-footer sidebar-footer-column">
        <div className="sidebar-system-row">
          <div className="system-dot" />

          <div>
            <strong>SmartPark UCE</strong>
            <span>
              {isGuard
                ? "Garita 01 · Edge + AWS"
                : "Administración cloud"}
            </span>
          </div>
        </div>

        <button
          className="sidebar-logout"
          type="button"
          onClick={logout}
        >
          <LogOut size={17} />
          Salir de la vista
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
