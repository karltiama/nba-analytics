'use client';

import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

interface DataQualityResponse {
  success: boolean;
  data: {
    summary: {
      teamsCount: number;
      gamesCount: number;
      teamStatsCount: number;
      dateRange: {
        earliest: string;
        latest: string;
      };
    };
    seasonBreakdown: Array<{
      season: string;
      seasonType: string;
      gameCount: number;
    }>;
    teamsByConference: Array<{
      conference: string;
      teamCount: number;
    }>;
  };
}

const DataQualityDashboard = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['data-quality'],
    queryFn: async () => {
      const response = await fetch('/api/data-quality');
      return response.json();
    }
  });

  if (isLoading) {
    return (
      <div className="p-4">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">Error loading data quality metrics</p>
        </div>
      </div>
    );
  }

  const qualityData = data?.data;
  if (!qualityData) return null;

  const { summary, seasonBreakdown, teamsByConference } = qualityData;

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-6">Data Quality Dashboard</h2>
      
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-blue-800">Teams</h3>
          <p className="text-3xl font-bold text-blue-600">{summary.teamsCount}</p>
          <p className="text-sm text-blue-600">NBA Teams</p>
        </div>
        
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-green-800">Games</h3>
          <p className="text-3xl font-bold text-green-600">{summary.gamesCount.toLocaleString()}</p>
          <p className="text-sm text-green-600">Total Games</p>
        </div>
        
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-purple-800">Team Stats</h3>
          <p className="text-3xl font-bold text-purple-600">{summary.teamStatsCount}</p>
          <p className="text-sm text-purple-600">Season Records</p>
        </div>
        
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-orange-800">Date Range</h3>
          <p className="text-sm font-bold text-orange-600">
            {new Date(summary.dateRange.earliest).getFullYear()} - {new Date(summary.dateRange.latest).getFullYear()}
          </p>
          <p className="text-sm text-orange-600">Years Covered</p>
        </div>
      </div>

      {/* Conference Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Teams by Conference</h3>
          <div className="space-y-2">
            {teamsByConference.map((conf) => (
              <div key={conf.conference} className="flex justify-between items-center">
                <span className="font-medium">{conf.conference}</span>
                <span className="bg-gray-100 px-3 py-1 rounded-full text-sm font-semibold">
                  {conf.teamCount} teams
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Recent Seasons</h3>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {seasonBreakdown.slice(0, 10).map((season) => (
              <div key={`${season.season}-${season.seasonType}`} className="flex justify-between items-center">
                <span className="text-sm">
                  {season.season} {season.seasonType}
                </span>
                <span className="bg-gray-100 px-2 py-1 rounded text-xs font-semibold">
                  {season.gameCount} games
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Data Quality Indicators */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Data Quality Indicators</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm">Teams: {summary.teamsCount === 30 ? 'Complete' : 'Incomplete'}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm">Games: {summary.gamesCount > 10000 ? 'Good Coverage' : 'Limited'}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm">Stats: {summary.teamStatsCount > 300 ? 'Complete' : 'Incomplete'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataQualityDashboard;
