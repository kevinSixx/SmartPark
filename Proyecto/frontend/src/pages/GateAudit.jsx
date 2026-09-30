import { RefreshCw, X } from "lucide-react"
import { useEffect, useMemo, useState } from "react"

import { getGateActions, getStaffAccounts } from "../api/smartpark"
import TableFilters from "../components/TableFilters"

const display = (value) => value === null || value === undefined || value === "" ? "—" : String(value)

async function fetchAudit() {
  const [actions, staff] = await Promise.all([
    getGateActions("gate-01", 100),
    getStaffAccounts().catch(() => []),
  ])
  return {
    actions: Array.isArray(actions) ? actions : [],
    staffById: Object.fromEntries((Array.isArray(staff) ? staff : []).map((person) => [person.id, person])),
  }
}

function formatDateTime(value) {
  if (!value) return "—"
  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? display(value)
    : new Intl.DateTimeFormat("es-EC", { dateStyle: "medium", timeStyle: "short" }).format(date)
}

function GateAudit() {
  const [actions, setActions] = useState([])
  const [staffById, setStaffById] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [query, setQuery] = useState("")
  const [source, setSource] = useState("")
  const [action, setAction] = useState("")
  const [status, setStatus] = useState("")
  const [operatorFilter, setOperatorFilter] = useState("")
  const [reasonFilter, setReasonFilter] = useState("")
  const [selected, setSelected] = useState(null)

  async function load() {
    try {
      setLoading(true)
      setError("")
      const data = await fetchAudit()
      setActions(data.actions)
      setStaffById(data.staffById)
    } catch {
      setError("No se pudo cargar la auditoría de barrera. Inténtalo nuevamente.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAudit()
      .then((data) => {
        setActions(data.actions)
        setStaffById(data.staffById)
      })
      .catch(() => setError("No se pudo cargar la auditoría de barrera. Inténtalo nuevamente."))
      .finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => actions.filter((item) => {
    const operator = item.staff?.full_name || item.staff?.username || staffById[item.staff_id]?.full_name || staffById[item.staff_id]?.username || item.staff_name || item.operator_name || item.username || item.staff_id || ""
    const matchesText = [operator, item.reason, item.observation]
      .some((value) => String(value || "").toLocaleLowerCase().includes(query.trim().toLocaleLowerCase()))
    return matchesText && (!operatorFilter || String(item.staff_id ?? item.staff?.id ?? "") === operatorFilter)
      && (!reasonFilter || item.reason === reasonFilter)
      && (!source || item.source === source)
      && (!action || item.action === action) && (!status || item.status === status)
  }), [actions, staffById, query, operatorFilter, reasonFilter, source, action, status])

  function operatorName(item) {
    return display(item.staff?.full_name || item.staff?.username || staffById[item.staff_id]?.full_name || staffById[item.staff_id]?.username || item.staff_name || item.operator_name || item.username || (item.staff_id ? `Personal #${item.staff_id}` : null))
  }

  const fields = selected && [
    ["Fecha y hora", formatDateTime(selected.timestamp)],
    ["Guardia / operador", operatorName(selected)],
    ["Acción", display(selected.action)],
    ["Origen", display(selected.source)],
    ["Motivo", display(selected.reason)],
    ["Observación", display(selected.observation)],
    ["Estado", display(selected.status)],
    ["Evento relacionado", selected.access_event_id ? `#${selected.access_event_id}` : "—"],
  ]

  return (
    <section>
      <div className="page-heading row-heading">
        <div>
          <p className="eyebrow">Administración</p>
          <h2>Auditoría de barrera</h2>
          <p>Acciones registradas para Garita 01.</p>
        </div>
        <button className="secondary-button" type="button" onClick={load} disabled={loading}>
          <RefreshCw size={18} className={loading ? "spin" : ""} />
          {loading ? "Actualizando..." : "Actualizar"}
        </button>
      </div>
      {error && <div className="alert error">{error}</div>}
      <article className="panel">
        <div className="panel-header">
          <div>
            <h3>Acciones de Garita 01</h3>
            <p>Selecciona un registro para ver el detalle.</p>
          </div>
        </div>
        <TableFilters
          query={query} onQueryChange={setQuery}
          placeholder="Buscar guardia, motivo u observación"
          count={filtered.length}
          filters={[
            { label: "Guardia", value: operatorFilter, onChange: setOperatorFilter, options: [...new Set(actions.map((item) => item.staff_id ?? item.staff?.id).filter((id) => id != null))].map((id) => ({ value: String(id), label: staffById[id]?.full_name || staffById[id]?.username || `Personal #${id}` })) },
            { label: "Motivo", value: reasonFilter, onChange: setReasonFilter, options: [...new Set(actions.map((item) => item.reason).filter(Boolean))].map((reason) => ({ value: reason, label: reason })) },
            { label: "Origen", value: source, onChange: setSource, options: [{ value: "MANUAL", label: "MANUAL" }, { value: "AUTO", label: "AUTO" }] },
            { label: "Acción", value: action, onChange: setAction, options: [{ value: "OPEN", label: "OPEN" }, { value: "CLOSE", label: "CLOSE" }] },
            { label: "Estado", value: status, onChange: setStatus, options: [{ value: "SUCCESS", label: "SUCCESS" }, { value: "ERROR", label: "ERROR" }] },
          ]}
        />
        {loading && actions.length === 0 ? <div className="empty-state">Cargando acciones...</div>
          : filtered.length === 0 ? <div className="empty-state">{actions.length ? "No hay acciones que coincidan con los filtros." : "No hay acciones de barrera registradas."}</div>
            : <div className="table-wrapper admin-table-scroll">
              <table>
                <thead><tr>
                  <th>Fecha / hora</th><th>Guardia / operador</th><th>Acción</th><th>Origen</th>
                  <th>Motivo</th><th>Observación</th><th>Estado</th><th>Evento relacionado</th>
                </tr></thead>
                <tbody>{filtered.map((item, index) => <tr key={item.id ?? index} className="gate-audit-row" onClick={() => setSelected(item)}>
                  <td><button className="table-row-link" type="button" onClick={() => setSelected(item)}>{formatDateTime(item.timestamp)}</button></td>
                  <td>{operatorName(item)}</td><td>{display(item.action)}</td><td>{display(item.source)}</td>
                  <td>{display(item.reason)}</td><td>{display(item.observation)}</td>
                  <td><span className={`permission-state ${item.status === "SUCCESS" ? "valid" : item.status === "ERROR" ? "expired" : "inactive"}`}>{display(item.status)}</span></td>
                  <td>{item.access_event_id ? `#${item.access_event_id}` : "—"}</td>
                </tr>)}</tbody>
              </table>
            </div>}
      </article>
      {selected && <div className="modal-backdrop" onClick={() => setSelected(null)}>
        <div className="modal-card gate-audit-modal" role="dialog" aria-modal="true" aria-label="Detalle de acción de barrera" onClick={(event) => event.stopPropagation()}>
          <div className="modal-header">
            <div><p className="eyebrow">Garita 01</p><h3>Detalle de acción</h3></div>
            <button className="modal-close" type="button" aria-label="Cerrar detalle" onClick={() => setSelected(null)}><X size={20} /></button>
          </div>
          <dl className="gate-audit-details">{fields.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
        </div>
      </div>}
    </section>
  )
}

export default GateAudit
