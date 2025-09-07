'use client';

import { AgGridReact } from 'ag-grid-react';
import { ColDef } from 'ag-grid-community';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

interface Team {
  id: string;
  name: string;
  abbreviation: string;
  city: string;
  conference: string;
  division: string;
  logoUrl?: string;
  createdAt: string;
}

interface TeamsResponse {
  success: boolean;
  data: Team[];
}

const TeamsTable = () => {
  const [conferenceFilter, setConferenceFilter] = useState<string>('');
  const [divisionFilter, setDivisionFilter] = useState<string>('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['teams', conferenceFilter, divisionFilter],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (conferenceFilter) params.append('conference', conferenceFilter);
      if (divisionFilter) params.append('division', divisionFilter);
      
      const response = await fetch(`/api/teams?${params.toString()}`);
      return response.json();
    }
  });

  const columnDefs: ColDef<Team>[] = [
    {
      field: 'abbreviation',
      headerName: 'Team',
      width: 80,
      pinned: 'left',
      cellRenderer: (params: any) => {
        const team = params.data;
        return (
          <div className="flex items-center gap-2">
            {team.logoUrl && (
              <img 
                src={team.logoUrl} 
                alt={team.name}
                className="w-6 h-6"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = 'none';
                }}
              />
            )}
            <span className="font-semibold">{team.abbreviation}</span>
          </div>
        );
      }
    },
    {
      field: 'city',
      headerName: 'City',
      width: 120
    },
    {
      field: 'name',
      headerName: 'Name',
      width: 120
    },
    {
      field: 'conference',
      headerName: 'Conference',
      width: 100,
      cellRenderer: (params: any) => {
        const conference = params.value;
        const color = conference === 'Eastern' ? 'text-blue-600' : 'text-red-600';
        return <span className={`font-medium ${color}`}>{conference}</span>;
      }
    },
    {
      field: 'division',
      headerName: 'Division',
      width: 120
    },
    {
      field: 'createdAt',
      headerName: 'Added',
      width: 100,
      cellRenderer: (params: any) => {
        return new Date(params.value).toLocaleDateString();
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
          <p className="text-red-800">Error loading teams data</p>
        </div>
      </div>
    );
  }

  const teams = data?.data || [];

  return (
    <div className="p-4">
      <div className="mb-4">
        <h2 className="text-xl font-bold mb-4">NBA Teams ({teams.length})</h2>
        
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
            value={divisionFilter}
            onChange={(e) => setDivisionFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">All Divisions</option>
            <option value="Atlantic">Atlantic</option>
            <option value="Central">Central</option>
            <option value="Southeast">Southeast</option>
            <option value="Northwest">Northwest</option>
            <option value="Pacific">Pacific</option>
            <option value="Southwest">Southwest</option>
          </select>
        </div>
      </div>

      <div className="ag-theme-alpine" style={{ height: '400px', width: '100%' }}>
        <AgGridReact
          rowData={teams}
          columnDefs={columnDefs}
          theme="legacy"
          defaultColDef={{
            sortable: true,
            filter: true,
            resizable: true
          }}
          pagination={true}
          paginationPageSize={20}
          suppressRowClickSelection={true}
        />
      </div>
    </div>
  );
};

export default TeamsTable;
