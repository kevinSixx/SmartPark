import {
  Navigate,
  useLocation,
} from "react-router-dom"

import {
  getSession,
} from "../utils/session"


function RequireRole({
  allowedRoles,
  children,
}) {
  const location = useLocation()
  const session = getSession()
  const role = String(session?.role || "").toUpperCase()

  if (!session) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location.pathname }}
      />
    )
  }

  if (!allowedRoles.includes(role)) {
    return (
      <Navigate
        to={role === "GUARD" ? "/guard" : "/admin"}
        replace
      />
    )
  }

  return children
}

export default RequireRole
