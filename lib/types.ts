// Type definitions for NBA Analytics

export interface Team {
  id: string
  name: string
  abbreviation: string
  city: string
  conference: string
  division: string
  logoUrl?: string
}

export interface Player {
  id: string
  name: string
  position: string
  height?: number
  weight?: number
  jerseyNumber?: number
  teamId?: string
  isActive: boolean
  team?: Team
}

export interface TeamStats {
  id: string
  teamId: string
  season: string
  gamesPlayed: number
  wins: number
  losses: number
  pointsPerGame: number
  pointsAllowed: number
  fieldGoalPct: number
  threePointPct: number
  freeThrowPct: number
  rebounds: number
  assists: number
  turnovers: number
  steals: number
  blocks: number
  team?: Team
}

export interface PlayerStats {
  id: string
  playerId: string
  season: string
  gamesPlayed: number
  minutesPerGame: number
  pointsPerGame: number
  rebounds: number
  assists: number
  steals: number
  blocks: number
  turnovers: number
  fieldGoalPct: number
  threePointPct: number
  freeThrowPct: number
  player?: Player
}

export interface Game {
  id: string
  gameDate: Date
  season: string
  seasonType: string
  homeTeamId: string
  awayTeamId: string
  homeScore?: number
  awayScore?: number
  status: string
  attendance?: number
  venue?: string
  homeTeam?: Team
  awayTeam?: Team
}


