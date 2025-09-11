'use client';

import { AgGridReact } from 'ag-grid-react';
import { ColDef } from 'ag-grid-community';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

interface PlayerStats {
  id: string;
  season: string;
  seasonType: string;
  player: {
    id: string;
    name: string;
    position: string;
    team: {
      id: string;
      name: string;
      abbreviation: string;
      city: string;
      conference: string;
      division: string;
    } | null;
  };
  gamesPlayed: number;
  minutesPerGame: string;
  pointsPerGame: string;
  rebounds: string;
  assists: string;
  steals: string;
  blocks: string;
  turnovers: string;
  fieldGoalPct: string;
  threePointPct: string;
  freeThrowPct: string;
}

interface PlayerStatsResponse {
  success: boolean;
  data: PlayerStats[];
}

interface PlayerStatsBySeasonTypeProps {
  season: string;
  seasonType: 'Regular Season' | 'Playoffs' | 'Preseason';
  height?: string;
  title?: string;
}

const PlayerStatsBySeasonType = ({ 
  season, 
  seasonType, 
  height = '500px',
  title
}: PlayerStatsBySeasonTypeProps) => {
  const [teamFilter, setTeamFilter] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('pointsPerGame');

  const { data, isLoading, error } = useQuery({
    queryKey: ['player-stats-by-type', season, seasonType, teamFilter, sortBy],
    queryFn: async () => {
      const params = new URLSearchParams();
      params.append('season', season);
      params.append('seasonType', seasonType);
      if (teamFilter) params.append('teamId', teamFilter);
      params.append('sortBy', sortBy);
      params.append('limit', '50');
      
      const response = await fetch(`/api/player-stats-by-type?${params.toString()}`);
      return response.json();
    }
  });

  const columnDefs: ColDef<PlayerStats>[] = [
    {
      field: 'player',
      headerName: 'Player',
      width: 180,
      pinned: 'left',
      cellRenderer: (params: any) => {
        const player = params.value;
        return (
          <div className="flex flex-col">
            <span className="font-semibold">{player.name}</span>
            <span className="text-xs text-black">
              {player.position} • {player.team?.abbreviation || 'Free Agent'}
            </span>
          </div>
        );
      }
    },
    {
      field: 'gamesPlayed',
      headerName: 'Games Played',
      width: 100,
      cellStyle: { textAlign: 'center' }
    },
    {
      field: 'minutesPerGame',
      headerName: 'Minutes Per Game',
      width: 130,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        return <span className="font-mono">{params.value}</span>;
      }
    },
    {
      field: 'pointsPerGame',
      headerName: 'Points Per Game',
      width: 130,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        return <span className="font-mono font-semibold text-blue-600">{params.value}</span>;
      }
    },
    {
      field: 'rebounds',
      headerName: 'Rebounds Per Game',
      width: 140,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        return <span className="font-mono">{params.value}</span>;
      }
    },
    {
      field: 'assists',
      headerName: 'Assists Per Game',
      width: 130,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        return <span className="font-mono">{params.value}</span>;
      }
    },
    {
      field: 'steals',
      headerName: 'Steals Per Game',
      width: 130,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        return <span className="font-mono">{params.value}</span>;
      }
    },
    {
      field: 'blocks',
      headerName: 'Blocks Per Game',
      width: 130,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        return <span className="font-mono">{params.value}</span>;
      }
    },
    {
      field: 'turnovers',
      headerName: 'Turnovers Per Game',
      width: 140,
      cellStyle: { textAlign: 'center' },
      cellRenderer: (params: any) => {
        return <span className="font-mono">{params.value}</span>;
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
          <p className="text-red-800">Error loading {seasonType.toLowerCase()} player stats data</p>
        </div>
      </div>
    );
  }

  const stats = data?.data || [];

  return (
    <div className="p-4">
      <div className="mb-4">
        <h3 className="text-lg font-bold mb-4">
          {title || `${seasonType} - ${season}`} ({stats.length} players)
        </h3>
        
        {/* Filters */}
        <div className="flex gap-4 mb-4">
          <select
            value={teamFilter}
            onChange={(e) => setTeamFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">All Teams</option>
            <option value="Eastern">Eastern Conference</option>
            <option value="Western">Western Conference</option>
          </select>
          
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="pointsPerGame">Sort by PPG</option>
            <option value="rebounds">Sort by RPG</option>
            <option value="assists">Sort by APG</option>
            <option value="gamesPlayed">Sort by Games</option>
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

export default PlayerStatsBySeasonType;

