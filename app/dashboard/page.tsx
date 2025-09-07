'use client'

import { useState, useEffect } from 'react'
import TeamStatsTable from '@/components/tables/TeamStatsTable'
import TeamStatsBySeasonType from '@/components/tables/TeamStatsBySeasonType'
import PlayerStatsTable from '@/components/tables/PlayerStatsTable'
import { TeamStats, PlayerStats } from '@/lib/types'

export default function Dashboard() {
  const [playerStats, setPlayerStats] = useState<PlayerStats[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedSeason, setSelectedSeason] = useState('2024-25')

  useEffect(() => {
    fetchData()
  }, [selectedSeason])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch player stats
      const playerResponse = await fetch(`/api/player-stats?season=${selectedSeason}&limit=50`)
      const playerData = await playerResponse.json()
      
      if (!playerData.success) {
        throw new Error(playerData.error || 'Failed to fetch player stats')
      }
      setPlayerStats(playerData.data)

    } catch (err) {
      console.error('Error fetching data:', err)
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const seasons = ['2024-25', '2023-24', '2022-23', '2021-22', '2020-21', '2019-20']

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-300">Loading NBA data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-white mb-2">Error Loading Data</h2>
          <p className="text-gray-300 mb-4">{error}</p>
          <button 
            onClick={fetchData}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

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

          {/* Player Stats Section */}
          <div className="bg-gray-800 rounded-xl shadow-lg border border-gray-700 overflow-hidden">
            <div className="px-6 py-5 bg-gradient-to-r from-green-600 to-green-700 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold">Player Statistics - {selectedSeason}</h2>
                  <p className="text-green-100 mt-1">
                    {playerStats.length} players • Sorted by Points Per Game
                  </p>
                </div>
                <div className="text-4xl">👤</div>
              </div>
            </div>
            <div className="p-6 bg-gray-900">
              <PlayerStatsTable data={playerStats} height="600px" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

