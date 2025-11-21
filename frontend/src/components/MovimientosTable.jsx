import { useEffect, useMemo, useRef, useState } from 'react'
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getExpandedRowModel,
  getGroupedRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable
} from '@tanstack/react-table'

/**
 * Tabla avanzada para explorar movimientos.
 * Incluye selección, agrupación, ordenación server-side y edición inline.
 */
export default function MovimientosTable({
  data,
  isLoading,
  sorting,
  onSortChange,
  grouping,
  onGroupChange,
  onInlineUpdate,
  categories,
  aggregates,
  onRowClick,
  selectedRowId
}) {
  const columnHelper = createColumnHelper()
  const [columnVisibility, setColumnVisibility] = useState({})
  const [rowSelection, setRowSelection] = useState({})
  const [editableCell, setEditableCell] = useState(null)
  const [tableData, setTableData] = useState(data || [])
  const tableRef = useRef(null)
  const [focusIndex, setFocusIndex] = useState(-1)

  useEffect(() => {
    setTableData(data || [])
  }, [data])

  const renderEditableSelect = (row, field) => {
    const isEditing = editableCell?.rowId === row.original.id && editableCell?.field === field
    if (!isEditing) {
      return (
        <button className="inline-edit" onClick={() => setEditableCell({ rowId: row.original.id, field })}>
          {row.original[field] || 'Asignar'}
        </button>
      )
    }
    return (
      <select
        autoFocus
        value={row.original.categoria_id || ''}
        onChange={async (e) => {
          if (!e.target.value) {
            setEditableCell(null)
            return
          }
          const categoriaId = Number(e.target.value)
          await onInlineUpdate(row.original.id, { categoria_id: categoriaId })
          setEditableCell(null)
        }}
        onBlur={() => setEditableCell(null)}
      >
        <option value="">Sin categoría</option>
        {categories?.map((cat) => (
          <option key={cat.id} value={cat.id}>{cat.nombre}</option>
        ))}
      </select>
    )
  }

  const renderEditableInput = (row, field) => {
    const isEditing = editableCell?.rowId === row.original.id && editableCell?.field === field
    if (!isEditing) {
      return (
        <button className="inline-edit" onClick={() => setEditableCell({ rowId: row.original.id, field })}>
          {row.original[field] || 'Añadir nota'}
        </button>
      )
    }
    return (
      <input
        autoFocus
        defaultValue={row.original[field] || ''}
        onBlur={(e) => handleInlineInput(row, field, e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') handleInlineInput(row, field, e.target.value)
          if (e.key === 'Escape') setEditableCell(null)
        }}
      />
    )
  }

  const handleInlineInput = async (row, field, value) => {
    await onInlineUpdate(row.original.id, { [field]: value })
    setEditableCell(null)
  }

  const columns = useMemo(() => {
    return [
      {
        id: 'select',
        header: () => <input type="checkbox" checked={Object.keys(rowSelection).length === tableData.length && tableData.length > 0} onChange={(e) => {
          if (e.target.checked) {
            const all = tableData.reduce((acc, _, idx) => ({ ...acc, [idx]: true }), {})
            setRowSelection(all)
          } else {
            setRowSelection({})
          }
        }} />,
        cell: ({ row }) => (
          <input
            type="checkbox"
            checked={row.getIsSelected()}
            onChange={row.getToggleSelectedHandler()}
          />
        ),
        size: 30
      },
      columnHelper.accessor('fecha', {
        header: 'Fecha',
        sortingFn: 'datetime'
      }),
      columnHelper.accessor('concepto', {
        header: 'Concepto'
      }),
      columnHelper.accessor('importe', {
        header: 'Importe',
        cell: (info) => <span className={info.getValue() < 0 ? 'text-negative' : 'text-positive'}>{info.getValue().toFixed(2)}</span>
      }),
      columnHelper.accessor('saldo', { header: 'Saldo' }),
      columnHelper.accessor('tipo_nombre', { header: 'Tipo' }),
      columnHelper.accessor('mes_anio', { header: 'Mes' }),
      columnHelper.accessor('categoria_nombre', {
        header: 'Categoría',
        cell: ({ row }) => renderEditableSelect(row, 'categoria_nombre')
      }),
      columnHelper.accessor('metodo_pago_nombre', {
        header: 'Método pago',
        cell: ({ row }) => row.original.metodo_pago_nombre || '—'
      }),
      columnHelper.accessor('notas', {
        header: 'Notas',
        cell: ({ row }) => renderEditableInput(row, 'notas')
      })
    ]
  }, [columnHelper, rowSelection, tableData, categories])

  const table = useReactTable({
    data: tableData,
    columns,
    state: {
      sorting: sorting ? [{ id: sorting.id, desc: sorting.desc }] : [],
      columnVisibility,
      grouping,
      rowSelection
    },
    manualSorting: true,
    onSortingChange: (updater) => {
      const next = typeof updater === 'function' ? updater(table.getState().sorting) : updater
      const newSorting = next?.[0]
      onSortChange(newSorting ? { id: newSorting.id, desc: !!newSorting.desc } : null)
    },
    onColumnVisibilityChange: setColumnVisibility,
    onGroupingChange: onGroupChange,
    onRowSelectionChange: setRowSelection,
    enableRowSelection: true,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getGroupedRowModel: getGroupedRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
    getPaginationRowModel: getPaginationRowModel()
  })

  useEffect(() => {
    const el = tableRef.current
    const handler = (e) => {
      if (!el || !el.contains(document.activeElement)) return
      const rows = table.getRowModel().rows
      if (!rows.length) return
      if (['j', 'ArrowDown'].includes(e.key)) {
        const next = Math.min(rows.length - 1, focusIndex + 1)
        setFocusIndex(next)
        onRowClick?.(rows[next].original)
      }
      if (['k', 'ArrowUp'].includes(e.key)) {
        const prev = Math.max(0, focusIndex - 1)
        setFocusIndex(prev)
        onRowClick?.(rows[prev].original)
      }
      if (e.key === 'Enter' && focusIndex >= 0) {
        onRowClick?.(rows[focusIndex].original)
      }
      if (e.key === 'Escape') {
        setFocusIndex(-1)
        setRowSelection({})
        onRowClick?.(null)
      }
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [focusIndex, onRowClick, table])

  useEffect(() => {
    if (!selectedRowId) return
    const idx = tableData.findIndex((row) => row.id === selectedRowId)
    if (idx >= 0) setFocusIndex(idx)
  }, [selectedRowId, tableData])

  const selectedRows = table.getSelectedRowModel().flatRows
  const selectedSum = selectedRows.reduce((acc, row) => acc + (row.original.importe || 0), 0)
  const pageTotal = tableData.reduce((acc, row) => acc + (row.importe || 0), 0)
  const pageCount = tableData.length

  return (
    <div className="card" ref={tableRef} tabIndex={0}>
      <div className="table-actions">
        <div className="grouping">
          <label>Agrupar por:</label>
          <select value={grouping?.[0] || ''} onChange={(e) => onGroupChange(e.target.value ? [e.target.value] : [])}>
            <option value="">Sin agrupación</option>
            <option value="categoria_nombre">Categoría</option>
            <option value="mes_anio">Mes</option>
          </select>
        </div>
        <div className="column-toggle">
          <details>
            <summary>Columnas</summary>
            {table.getAllLeafColumns().map((column) => (
              <label key={column.id} style={{ display: 'block' }}>
                <input
                  type="checkbox"
                  checked={column.getIsVisible()}
                  onChange={column.getToggleVisibilityHandler()}
                />{' '}
                {column.columnDef.header}
              </label>
            ))}
          </details>
        </div>
      </div>
      <div className="table-wrapper">
        <table className="table">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    onClick={header.column.getCanSort() ? header.column.getToggleSortingHandler() : undefined}
                    style={{ cursor: header.column.getCanSort() ? 'pointer' : 'default' }}
                  >
                    {flexRender(header.column.columnDef.header, header.getContext())}
                    {{ asc: ' ▲', desc: ' ▼' }[header.column.getIsSorted() ?? null] ?? null}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {isLoading && (
              <tr>
                <td colSpan={columns.length} style={{ textAlign: 'center' }}>
                  Cargando movimientos...
                </td>
              </tr>
            )}
            {!isLoading && table.getRowModel().rows.map((row) => (
              <tr key={row.id} className={row.original.id === selectedRowId ? 'row-selected' : ''} onClick={() => onRowClick?.(row.original)}>
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="table-footer">
        <div>
          <strong>Totales página:</strong> {pageCount} filas · {pageTotal.toFixed(2)}
        </div>
        <div>
          <strong>Seleccionados:</strong> {selectedRows.length} · {selectedSum.toFixed(2)}
        </div>
        <div>
          <strong>Agregados globales:</strong> ingresos {aggregates?.total_ingresos?.toFixed(2)} / gastos {aggregates?.total_gastos?.toFixed(2)}
        </div>
      </div>
    </div>
  )
}
