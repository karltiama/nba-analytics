'use client'

import { AgGridReact } from 'ag-grid-react'
import { ColDef, GridOptions, ModuleRegistry, AllCommunityModule, themeQuartz } from 'ag-grid-community'
import 'ag-grid-community/styles/ag-theme-quartz.css'

// Register AG Grid modules
ModuleRegistry.registerModules([AllCommunityModule])

// Create custom dark theme
const nbaDarkTheme = themeQuartz
  .withParams({
    backgroundColor: "#1f2836",
    browserColorScheme: "dark",
    chromeBackgroundColor: {
      ref: "foregroundColor",
      mix: 0.07,
      onto: "backgroundColor"
    },
    foregroundColor: "#FFF",
    headerFontSize: 14
  })

interface AgGridTableProps {
  data: any[]
  columnDefs: ColDef[]
  gridOptions?: GridOptions
  height?: string
  className?: string
}

export default function AgGridTable({ 
  data, 
  columnDefs, 
  gridOptions = {},
  height = '400px',
  className = ''
}: AgGridTableProps) {
  const defaultGridOptions: GridOptions = {
    defaultColDef: {
      sortable: true,
      filter: true,
      resizable: true,
      flex: 1,
      minWidth: 100,
    },
    pagination: true,
    paginationPageSize: 20,
    paginationPageSizeSelector: [10, 20, 50, 100],
    suppressRowHoverHighlight: false,
    rowSelection: 'single',
    animateRows: true,
    ...gridOptions
  }

  return (
    <div className={`ag-theme-quartz nba-analytics-grid ${className}`} style={{ height, width: '100%' }}>
      <AgGridReact
        theme={nbaDarkTheme}
        rowData={data}
        columnDefs={columnDefs}
        gridOptions={defaultGridOptions}
      />
    </div>
  )
}
