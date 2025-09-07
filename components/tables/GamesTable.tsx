'use client';

import { AgGridReact } from 'ag-grid-react';
import { ColDef } from 'ag-grid-community';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

interface Game {
  id: string;
  gameDate: string;
  season: string;
  seasonType: string;
  homeTeam: {
    id: string;
    name: string;
    abbreviation: string;
    city: string;
  };
  awayTeam: {
    id: string;
    name: string;
    abbreviation: string;
    city: string;
  };
  homeScore: number | null;
  awayScore: number | null;
  status: string;
  attendance: number | null;
  venue: string | null;
}

interface GamesResponse {
  success: boolean;
  data: Game[];
}

const GamesTable = () => {
  const [seasonFilter, setSeasonFilter] = useState<string>('');
  const [seasonTypeFilter, setSeasonTypeFilter] = useState<string>('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['games', seasonFilter, seasonTypeFilter],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (seasonFilter) params.append('season', seasonFilter);
      if (seasonTypeFilter) params.append('seasonType', seasonTypeFilter);
      params.append('limit', '100');
      
      const response = await fetch(`/api/games?${params.toString()}`);
      return response.json();
    }
  });

  const columnDefs: ColDef<Game>[] = [
    {
      field: 'gameDate',
      headerName: 'Date',
      width: 120,
      pinned: 'left',
      cellRenderer: (params: any) => {
        return new Date(params.value).toLocaleDateString();
      }
    },
    {
      field: 'season',
      headerName: 'Season',
      width: 80
    },
    {
      field: 'seasonType',
      headerName: 'Type',
      width: 100,
      cellRenderer: (params: any) => {
        const type = params.value;
        const colors = {
          'Regular Season': 'bg-blue-100 text-blue-800',
          'Playoffs': 'bg-purple-100 text-purple-800',
          'Preseason': 'bg-gray-100 text-gray-800'
        };
        const colorClass = colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800';
        return (
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${colorClass}`}>
            {type}
          </span>
        );
      }
    },
    {
      field: 'awayTeam',
      headerName: 'Away Team',
      width: 140,
      cellRenderer: (params: any) => {
        const team = params.value;
        return (
          <div className="flex items-center gap-2">
            <span className="font-medium">{team.abbreviation}</span>
            <span className="text-gray-500 text-sm">{team.city}</span>
          </div>
        );
      }
    },
    {
      field: 'awayScore',
      headerName: 'Away Score',
      width: 90,
      cellRenderer: (params: any) => {
        const score = params.value;
        return score !== null ? (
          <span className="font-mono font-semibold">{score}</span>
        ) : (
          <span className="text-gray-400">-</span>
        );
      }
    },
    {
      field: 'homeTeam',
      headerName: 'Home Team',
      width: 140,
      cellRenderer: (params: any) => {
        const team = params.value;
        return (
          <div className="flex items-center gap-2">
            <span className="font-medium">{team.abbreviation}</span>
            <span className="text-gray-500 text-sm">{team.city}</span>
          </div>
        );
      }
    },
    {
      field: 'homeScore',
      headerName: 'Home Score',
      width: 90,
      cellRenderer: (params: any) => {
        const score = params.value;
        return score !== null ? (
          <span className="font-mono font-semibold">{score}</span>
        ) : (
          <span className="text-gray-400">-</span>
        );
      }
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 80,
      cellRenderer: (params: any) => {
        const status = params.value;
        const colors = {
          'Final': 'bg-green-100 text-green-800',
          'Scheduled': 'bg-yellow-100 text-yellow-800',
          'In Progress': 'bg-blue-100 text-blue-800'
        };
        const colorClass = colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
        return (
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${colorClass}`}>
            {status}
          </span>
        );
      }
    },
    {
      field: 'attendance',
      headerName: 'Attendance',
      width: 100,
      cellRenderer: (params: any) => {
        const attendance = params.value;
        return attendance ? attendance.toLocaleString() : '-';
      }
    }
  ];

  if (isLoading) {
    return (
      <div className="p-4">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">Error loading games data</p>
        </div>
      </div>
    );
  }

  const games = data?.data || [];

  return (
    <div className="p-4">
      <div className="mb-4">
        <h2 className="text-xl font-bold mb-4">NBA Games ({games.length} shown)</h2>
        
        {/* Filters */}
        <div className="flex gap-4 mb-4">
          <select
            value={seasonFilter}
            onChange={(e) => setSeasonFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">All Seasons</option>
            <option value="2024-25">2024-25</option>
            <option value="2023-24">2023-24</option>
            <option value="2022-23">2022-23</option>
            <option value="2021-22">2021-22</option>
            <option value="2020-21">2020-21</option>
          </select>
          
          <select
            value={seasonTypeFilter}
            onChange={(e) => setSeasonTypeFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">All Types</option>
            <option value="Regular Season">Regular Season</option>
            <option value="Playoffs">Playoffs</option>
            <option value="Preseason">Preseason</option>
          </select>
        </div>
      </div>

      <div className="ag-theme-alpine" style={{ height: '500px', width: '100%' }}>
        <AgGridReact
          rowData={games}
          columnDefs={columnDefs}
          theme="legacy"
          defaultColDef={{
            sortable: true,
            filter: true,
            resizable: true
          }}
          pagination={true}
          paginationPageSize={25}
          suppressRowClickSelection={true}
        />
      </div>
    </div>
  );
};

export default GamesTable;
