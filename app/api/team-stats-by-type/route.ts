import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const season = searchParams.get('season');
    const seasonType = searchParams.get('seasonType');
    const conference = searchParams.get('conference');
    const division = searchParams.get('division');
    const limit = parseInt(searchParams.get('limit') || '100');
    const sortBy = searchParams.get('sortBy') || 'wins';

    if (!season || !seasonType) {
      return NextResponse.json(
        { success: false, error: 'Season and seasonType are required' },
        { status: 400 }
      );
    }

    // Get all teams
    const teams = await prisma.team.findMany({
      select: {
        id: true,
        name: true,
        abbreviation: true,
        city: true,
        conference: true,
        division: true
      }
    });

    // Filter teams by conference/division if specified
    let filteredTeams = teams;
    if (conference) {
      filteredTeams = filteredTeams.filter(team => team.conference === conference);
    }
    if (division) {
      filteredTeams = filteredTeams.filter(team => team.division === division);
    }

    // Calculate stats for each team
    const teamStatsPromises = filteredTeams.map(async (team) => {
      // Get games for this team in the specified season and season type
      const games = await prisma.game.findMany({
        where: {
          season: season,
          seasonType: seasonType,
          OR: [
            { homeTeamId: team.id },
            { awayTeamId: team.id }
          ]
        },
        select: {
          homeTeamId: true,
          awayTeamId: true,
          homeScore: true,
          awayScore: true
        }
      });

      // Calculate stats
      let wins = 0;
      let losses = 0;
      let totalPoints = 0;
      let totalPointsAllowed = 0;
      let gamesPlayed = 0;

      games.forEach(game => {
        if (game.homeScore !== null && game.awayScore !== null) {
          gamesPlayed++;
          
          if (game.homeTeamId === team.id) {
            // Team is home
            totalPoints += game.homeScore;
            totalPointsAllowed += game.awayScore;
            if (game.homeScore > game.awayScore) {
              wins++;
            } else {
              losses++;
            }
          } else {
            // Team is away
            totalPoints += game.awayScore;
            totalPointsAllowed += game.homeScore;
            if (game.awayScore > game.homeScore) {
              wins++;
            } else {
              losses++;
            }
          }
        }
      });

      // Get advanced stats from team_stats table (if available)
      const advancedStats = await prisma.teamStats.findFirst({
        where: {
          teamId: team.id,
          season: season
        }
      });

      return {
        id: `${team.id}-${season}-${seasonType}`,
        season: season,
        seasonType: seasonType,
        team: team,
        gamesPlayed: gamesPlayed,
        wins: wins,
        losses: losses,
        winPercentage: gamesPlayed > 0 ? (wins / gamesPlayed * 100).toFixed(1) : '0.0',
        pointsPerGame: gamesPlayed > 0 ? (totalPoints / gamesPlayed).toFixed(1) : '0.0',
        pointsAllowed: gamesPlayed > 0 ? (totalPointsAllowed / gamesPlayed).toFixed(1) : '0.0',
        pointDifferential: gamesPlayed > 0 ? ((totalPoints - totalPointsAllowed) / gamesPlayed).toFixed(1) : '0.0',
        fieldGoalPct: advancedStats ? (advancedStats.fieldGoalPct * 100).toFixed(1) : '0.0',
        threePointPct: advancedStats ? (advancedStats.threePointPct * 100).toFixed(1) : '0.0',
        freeThrowPct: advancedStats ? (advancedStats.freeThrowPct * 100).toFixed(1) : '0.0',
        rebounds: advancedStats ? advancedStats.rebounds.toFixed(1) : '0.0',
        assists: advancedStats ? advancedStats.assists.toFixed(1) : '0.0',
        turnovers: advancedStats ? advancedStats.turnovers.toFixed(1) : '0.0',
        steals: advancedStats ? advancedStats.steals.toFixed(1) : '0.0',
        blocks: advancedStats ? advancedStats.blocks.toFixed(1) : '0.0'
      };
    });

    const allTeamStats = await Promise.all(teamStatsPromises);

    // Filter out teams with no games
    const teamStats = allTeamStats.filter(stat => stat.gamesPlayed > 0);

    // Sort the results
    teamStats.sort((a, b) => {
      switch (sortBy) {
        case 'wins':
          return b.wins - a.wins;
        case 'pointsPerGame':
          return parseFloat(b.pointsPerGame) - parseFloat(a.pointsPerGame);
        case 'season':
          return b.season.localeCompare(a.season);
        default:
          return b.wins - a.wins;
      }
    });

    // Apply limit
    const limitedStats = teamStats.slice(0, limit);

    return NextResponse.json({
      success: true,
      data: limitedStats
    });
  } catch (error) {
    console.error('Error fetching team stats by type:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch team stats by type' },
      { status: 500 }
    );
  }
}
