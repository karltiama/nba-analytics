'use client'

import { ColDef } from 'ag-grid-community'
import AgGridTable from '../AgGridTable'
import { PlayerStats } from '@/lib/types'

interface PlayerStatsTableProps {
  data: PlayerStats[]
  height?: string
}

export default function PlayerStatsTable({ data, height = '500px' }: PlayerStatsTableProps) {
  // Show message if no data
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-800 rounded-lg">
        <div className="text-center text-black">
          <div className="text-4xl mb-4">📊</div>
          <h3 className="text-lg font-semibold mb-2">No Player Data Available</h3>
          <p className="text-sm">Player statistics need to be imported from the CSV files.</p>
        </div>
      </div>
    )
  }

  const columnDefs: ColDef[] = [
    {
      headerName: 'Player',
      field: 'player.name',
      pinned: 'left',
      width: 150,
      cellRenderer: (params: any) => {
        const player = params.data.player
        return player?.name || 'Unknown'
      }
    },
    {
      headerName: 'Team',
      field: 'player.team.name',
      width: 120,
      cellRenderer: (params: any) => {
        const team = params.data.player?.team
        if (!team) {
          return 'Free Agent'
        }
        
        // Fix duplicate city names (e.g., "Milwaukee Milwaukee Bucks" -> "Milwaukee Bucks")
        const city = team.city || ''
        const name = team.name || ''
        
        // If the name already contains the city, just use the name
        if (name.toLowerCase().includes(city.toLowerCase())) {
          return name
        }
        
        // Otherwise, combine city and name
        return `${city} ${name}`.trim()
      },
      filter: 'agTextColumnFilter'
    },
    {
      headerName: 'Position',
      field: 'player.position',
      width: 80,
      filter: 'agTextColumnFilter'
    },
    {
      headerName: 'Games Played',
      field: 'gamesPlayed',
      width: 100,
      type: 'numericColumn'
    },
    {
      headerName: 'Minutes Per Game',
      field: 'minutesPerGame',
      width: 130,
      valueFormatter: (params: any) => params.value?.toFixed(1) || '0.0',
      type: 'numericColumn'
    },
    {
      headerName: 'Points Per Game',
      field: 'pointsPerGame',
      width: 130,
      valueFormatter: (params: any) => params.value?.toFixed(1) || '0.0',
      type: 'numericColumn'
    },
    {
      headerName: 'Rebounds Per Game',
      field: 'rebounds',
      width: 140,
      valueFormatter: (params: any) => params.value?.toFixed(1) || '0.0',
      type: 'numericColumn'
    },
    {
      headerName: 'Assists Per Game',
      field: 'assists',
      width: 130,
      valueFormatter: (params: any) => params.value?.toFixed(1) || '0.0',
      type: 'numericColumn'
    },
    {
      headerName: 'Steals Per Game',
      field: 'steals',
      width: 130,
      valueFormatter: (params: any) => params.value?.toFixed(1) || '0.0',
      type: 'numericColumn'
    },
    {
      headerName: 'Blocks Per Game',
      field: 'blocks',
      width: 130,
      valueFormatter: (params: any) => params.value?.toFixed(1) || '0.0',
      type: 'numericColumn'
    },
    {
      headerName: 'Turnovers Per Game',
      field: 'turnovers',
      width: 140,
      valueFormatter: (params: any) => params.value?.toFixed(1) || '0.0',
      type: 'numericColumn'
    },
    {
      headerName: 'Field Goal %',
      field: 'fieldGoalPct',
      width: 120,
      valueFormatter: (params: any) => `${(params.value * 100)?.toFixed(1) || '0.0'}%`,
      type: 'numericColumn'
    },
    {
      headerName: '3-Point %',
      field: 'threePointPct',
      width: 110,
      valueFormatter: (params: any) => `${(params.value * 100)?.toFixed(1) || '0.0'}%`,
      type: 'numericColumn'
    },
    {
      headerName: 'Free Throw %',
      field: 'freeThrowPct',
      width: 120,
      valueFormatter: (params: any) => `${(params.value * 100)?.toFixed(1) || '0.0'}%`,
      type: 'numericColumn'
    }
  ]

  return (
    <AgGridTable
      data={data}
      columnDefs={columnDefs}
      height={height}
      gridOptions={{
        defaultColDef: {
          sortable: true,
          filter: true,
          resizable: true,
          flex: 1,
          minWidth: 60,
        },
        pagination: true,
        paginationPageSize: 50,
        suppressRowHoverHighlight: false,
        rowSelection: 'single',
        animateRows: true,
      }}
    />
  )
}

