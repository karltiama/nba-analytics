'use client';

import { AgGridReact } from 'ag-grid-react';
import { ColDef } from 'ag-grid-community';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

interface TeamStats {
  id: string;
  season: string;
  team: {
    id: string;
    name: string;
    abbreviation: string;
    city: string;
    conference: string;
    division: string;
  };
  gamesPlayed: number;
  wins: number;
  losses: number;
  winPercentage: string;
  pointsPerGame: string;
  pointsAllowed: string;
  pointDifferential: string;
  fieldGoalPct: string;
  threePointPct: string;
  freeThrowPct: string;
  rebounds: string;
  assists: string;
  turnovers: string;
  steals: string;
  blocks: string;
}

interface TeamStatsResponse {
  success: boolean;
  data: TeamStats[];
}

interface TeamStatsBySeasonTypeProps {
  season: string;
  seasonType: 'Regular Season' | 'Playoffs' | 'Preseason';
  height?: string;
  title?: string;
}

const TeamStatsBySeasonType = ({ 
  season, 
  seasonType, 
  height = '500px',
  title
}: TeamStatsBySeasonTypeProps) => {
  const [conferenceFilter, setConferenceFilter] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('wins');

  const { data, isLoading, error } = useQuery({
    queryKey: ['team-stats-by-type', season, seasonType, conferenceFilter, sortBy],
    queryFn: async () => {
      const params = new URLSearchParams();
      params.append('season', season);
      params.append('seasonType', seasonType);
      if (conferenceFilter) params.append('conference', conferenceFilter);
      params.append('sortBy', sortBy);
      params.append('limit', '50');
      
      const response = await fetch(`/api/team-stats-by-type?${params.toString()}`);
      return response.json();
    }
  });

  const columnDefs: ColDef<TeamStats>[] = [
    {
      field: 'team',
      headerName: 'Team',
      width: 140,
      pinned: 'left',
      cellRenderer: (params: any) => {
        const team = params.value;
        return (
          <div className="flex flex-col">
            <span className="font-semibold">{team.abbreviation}</span>
            <span className="text-xs text-black">{team.city}</span>
          </div>
        );
      }
    },
    {
      field: 'wins',
      headerName: 'Wins',
      width: 80,
      cellStyle: { textAlign: 'center' }
    },
    {
      field: 'losses',
      headerName: 'Losses',
      width: 80,
      cellStyle: { textAlign: 'center' }
    },
    {
      field: 'winPercentage',
      headerName: 'Win %',
      width: 90,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        const winPct = parseFloat(params.value);
        const color = winPct >= 0.6 ? 'text-green-600' : winPct >= 0.5 ? 'text-blue-600' : 'text-red-600';
        return <span className={`font-semibold ${color}`}>{params.value}%</span>;
      }
    },
    {
      field: 'pointsPerGame',
      headerName: 'Points Per Game',
      width: 130,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        return <span className="font-mono">{params.value}</span>;
      }
    },
    {
      field: 'pointsAllowed',
      headerName: 'Points Allowed',
      width: 130,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        return <span className="font-mono">{params.value}</span>;
      }
    },
    {
      field: 'pointDifferential',
      headerName: 'Point Differential',
      width: 140,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        const diff = parseFloat(params.value);
        const color = diff > 0 ? 'text-green-600' : diff < 0 ? 'text-red-600' : 'text-black';
        return <span className={`font-mono font-semibold ${color}`}>{diff > 0 ? '+' : ''}{params.value}</span>;
      }
    },
    {
      field: 'fieldGoalPct',
      headerName: 'Field Goal %',
      width: 120,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        return <span className="font-mono">{params.value}%</span>;
      }
    },
    {
      field: 'threePointPct',
      headerName: '3-Point %',
      width: 110,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        return <span className="font-mono">{params.value}%</span>;
      }
    },
    {
      field: 'freeThrowPct',
      headerName: 'Free Throw %',
      width: 120,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        return <span className="font-mono">{params.value}%</span>;
      }
    },
    {
      field: 'rebounds',
      headerName: 'Rebounds',
      width: 100,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        return <span className="font-mono">{params.value}</span>;
      }
    },
    {
      field: 'assists',
      headerName: 'Assists',
      width: 90,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        return <span className="font-mono">{params.value}</span>;
      }
    },
    {
      field: 'turnovers',
      headerName: 'Turnovers',
      width: 100,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        return <span className="font-mono">{params.value}</span>;
      }
    },
    {
      field: 'steals',
      headerName: 'Steals',
      width: 90,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        return <span className="font-mono">{params.value}</span>;
      }
    },
    {
      field: 'blocks',
      headerName: 'Blocks',
      width: 90,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        return <span className="font-mono">{params.value}</span>;
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
          <p className="text-red-800">Error loading {seasonType.toLowerCase()} team stats data</p>
        </div>
      </div>
    );
  }

  const stats = data?.data || [];

  return (
    <div className="p-4">
      <div className="mb-4">
        <h3 className="text-lg font-bold mb-4">
          {title || `${seasonType} - ${season}`} ({stats.length} teams)
        </h3>
        
        {/* Filters */}
        <div className="flex gap-4 mb-4">
          <select
            value={conferenceFilter}
            onChange={(e) => setConferenceFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">All Conferences</option>
            <option value="Eastern">Eastern</option>
            <option value="Western">Western</option>
          </select>
          
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="wins">Sort by Wins</option>
            <option value="pointsPerGame">Sort by PPG</option>
            <option value="season">Sort by Season</option>
          </select>
        </div>
      </div>

      <div className="ag-theme-alpine" style={{ height, width: '100%' }}>
        <AgGridReact
          rowData={stats}
          columnDefs={columnDefs}
          theme="legacy"
          defaultColDef={{
            sortable: true,
            filter: true,
            resizable: true
          }}
          pagination={true}
          paginationPageSize={30}
          suppressRowClickSelection={true}
        />
      </div>
    </div>
  );
};

export default TeamStatsBySeasonType;
