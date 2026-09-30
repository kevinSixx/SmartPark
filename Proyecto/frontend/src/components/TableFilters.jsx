function TableFilters({
  query,
  onQueryChange,
  placeholder,
  filters = [],
  count,
}) {
  return (
    <div className="table-filters">
      <input
        type="search"
        aria-label="Buscar registros"
        placeholder={placeholder}
        value={query}
        onChange={(event) => onQueryChange(event.target.value)}
      />
      {filters.map(({ label, value, onChange, options }) => (
        <select
          key={label}
          aria-label={label}
          value={value}
          onChange={(event) => onChange(event.target.value)}
        >
          <option value="">{label}: todos</option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ))}
      <span className="table-filter-count">{count} resultados</span>
    </div>
  )
}

export default TableFilters
