'use client'

import { useState, useEffect } from 'react'
import TeamStatsTable from '@/components/tables/TeamStatsTable'
import TeamStatsBySeasonType from '@/components/tables/TeamStatsBySeasonType'
import PlayerStatsTable from '@/components/tables/PlayerStatsTable'
import PlayerStatsBySeasonType from '@/components/tables/PlayerStatsBySeasonType'
import { TeamStats, PlayerStats } from '@/lib/types'

export default function Dashboard() {
  const [selectedSeason, setSelectedSeason] = useState('2024-25')

  const seasons = ['2024-25', '2023-24', '2022-23', '2021-22', '2020-21', '2019-20']

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 shadow-lg border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-white">NBA Analytics Dashboard</h1>
              <p className="text-gray-300 mt-1">Team and Player Statistics</p>
            </div>
            <div className="flex items-center space-x-4">
              <label htmlFor="season-select" className="text-sm font-medium text-gray-300">
                Season:
              </label>
              <select
                id="season-select"
                value={selectedSeason}
                onChange={(e) => setSelectedSeason(e.target.value)}
                className="bg-gray-700 border border-gray-600 text-white rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {seasons.map(season => (
                  <option key={season} value={season}>{season}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Regular Season Team Stats Section */}
          <div className="bg-gray-800 rounded-xl shadow-lg border border-gray-700 overflow-hidden">
            <div className="px-6 py-5 bg-gradient-to-r from-blue-600 to-blue-700 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold">Regular Season - {selectedSeason}</h2>
                  <p className="text-blue-100 mt-1">
                    Regular Season Team Statistics • Sorted by Wins
                  </p>
                </div>
                <div className="text-4xl">🏀</div>
              </div>
            </div>
            <div className="p-6 bg-gray-900">
              <TeamStatsBySeasonType 
                season={selectedSeason} 
                seasonType="Regular Season" 
                height="500px" 
              />
            </div>
          </div>

          {/* Playoffs Team Stats Section */}
          <div className="bg-gray-800 rounded-xl shadow-lg border border-gray-700 overflow-hidden">
            <div className="px-6 py-5 bg-gradient-to-r from-purple-600 to-purple-700 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold">Playoffs - {selectedSeason}</h2>
                  <p className="text-purple-100 mt-1">
                    Playoff Team Statistics • Sorted by Wins
                  </p>
                </div>
                <div className="text-4xl">🏆</div>
              </div>
            </div>
            <div className="p-6 bg-gray-900">
              <TeamStatsBySeasonType 
                season={selectedSeason} 
                seasonType="Playoffs" 
                height="500px" 
              />
            </div>
          </div>

          {/* Regular Season Player Stats Section */}
          <div className="bg-gray-800 rounded-xl shadow-lg border border-gray-700 overflow-hidden">
            <div className="px-6 py-5 bg-gradient-to-r from-green-600 to-green-700 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold">Regular Season Players - {selectedSeason}</h2>
                  <p className="text-green-100 mt-1">
                    Regular Season Player Statistics • Sorted by Points Per Game
                  </p>
                </div>
                <div className="text-4xl">👤</div>
              </div>
            </div>
            <div className="p-6 bg-gray-900">
              <PlayerStatsBySeasonType 
                season={selectedSeason} 
                seasonType="Regular Season" 
                height="600px" 
              />
            </div>
          </div>

          {/* Playoffs Player Stats Section */}
          <div className="bg-gray-800 rounded-xl shadow-lg border border-gray-700 overflow-hidden">
            <div className="px-6 py-5 bg-gradient-to-r from-orange-600 to-orange-700 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold">Playoff Players - {selectedSeason}</h2>
                  <p className="text-orange-100 mt-1">
                    Playoff Player Statistics • Sorted by Points Per Game
                  </p>
                </div>
                <div className="text-4xl">🏆</div>
              </div>
            </div>
            <div className="p-6 bg-gray-900">
              <PlayerStatsBySeasonType 
                season={selectedSeason} 
                seasonType="Playoffs" 
                height="600px" 
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

