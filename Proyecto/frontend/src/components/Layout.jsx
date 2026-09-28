import {
  Outlet,
} from "react-router-dom"

import Header from "./Header"
import Sidebar from "./Sidebar"


function Layout({ role = "ADMIN" }) {
  return (
    <div className={
      `app-shell ${role === "GUARD" ? "guard-shell" : ""}`
    }>
      <Sidebar role={role} />

      <div className="app-main">
        <Header role={role} />

        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout
