import {
  Navigate,
  Route,
  Routes,
} from "react-router-dom"

import Layout from "./components/Layout"
import RequireRole from "./components/RequireRole"

import AccessControl from "./pages/AccessControl"
import AccessHistory from "./pages/AccessHistory"
import Dashboard from "./pages/Dashboard"
import FaceEnrollment from "./pages/FaceEnrollment"
import GateAudit from "./pages/GateAudit"
import GuardGate from "./pages/GuardGate"
import Login from "./pages/Login"
import Permissions from "./pages/Permissions"
import Staff from "./pages/Staff"
import Users from "./pages/Users"
import Vehicles from "./pages/Vehicles"


function AdminLayout() {
  return (
    <RequireRole allowedRoles={["ADMIN"]}>
      <Layout role="ADMIN" />
    </RequireRole>
  )
}

function GuardLayout() {
  return (
    <RequireRole allowedRoles={["ADMIN", "GUARD"]}>
      <Layout role="GUARD" />
    </RequireRole>
  )
}


function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={<Login />}
      />

      <Route element={<AdminLayout />}>
        <Route path="/admin" element={<Dashboard />} />
        <Route path="/admin/users" element={<Users />} />
        <Route
          path="/admin/users/:userId/face"
          element={<FaceEnrollment />}
        />
        <Route path="/admin/vehicles" element={<Vehicles />} />
        <Route path="/admin/permissions" element={<Permissions />} />
        <Route path="/admin/history" element={<AccessHistory />} />
        <Route path="/admin/gate-audit" element={<GateAudit />} />
        <Route path="/admin/access-test" element={<AccessControl />} />
        <Route path="/admin/staff" element={<Staff />} />
      </Route>

      <Route element={<GuardLayout />}>
        <Route path="/guard" element={<GuardGate />} />
        <Route path="/guard/history" element={<AccessHistory />} />
      </Route>

      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default App
