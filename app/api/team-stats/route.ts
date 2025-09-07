import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const season = searchParams.get('season');
    const conference = searchParams.get('conference');
    const division = searchParams.get('division');
    const limit = parseInt(searchParams.get('limit') || '100');
    const sortBy = searchParams.get('sortBy') || 'wins';

    // Build where clause
    const where: any = {};
    if (season) where.season = season;
    if (conference || division) {
      where.team = {};
      if (conference) where.team.conference = conference;
      if (division) where.team.division = division;
    }

    // Build order by clause
    const orderBy: any = {};
    if (sortBy === 'wins') orderBy.wins = 'desc';
    else if (sortBy === 'pointsPerGame') orderBy.pointsPerGame = 'desc';
    else if (sortBy === 'season') orderBy.season = 'desc';
    else orderBy.wins = 'desc';

    const teamStats = await prisma.teamStats.findMany({
      where,
      orderBy,
      take: limit,
      include: {
        team: {
          select: {
            id: true,
            name: true,
            abbreviation: true,
            city: true,
            conference: true,
            division: true
          }
        }
      }
    });

    // Format the response
    const formattedStats = teamStats.map(stat => ({
      id: stat.id,
      season: stat.season,
      team: {
        id: stat.team.id,
        name: stat.team.name,
        abbreviation: stat.team.abbreviation,
        city: stat.team.city,
        conference: stat.team.conference,
        division: stat.team.division
      },
      gamesPlayed: stat.gamesPlayed,
      wins: stat.wins,
      losses: stat.losses,
      winPercentage: stat.gamesPlayed > 0 ? (stat.wins / stat.gamesPlayed * 100).toFixed(1) : '0.0',
      pointsPerGame: stat.pointsPerGame.toFixed(1),
      pointsAllowed: stat.pointsAllowed.toFixed(1),
      pointDifferential: (stat.pointsPerGame - stat.pointsAllowed).toFixed(1),
      fieldGoalPct: (stat.fieldGoalPct * 100).toFixed(1),
      threePointPct: (stat.threePointPct * 100).toFixed(1),
      freeThrowPct: (stat.freeThrowPct * 100).toFixed(1),
      rebounds: stat.rebounds.toFixed(1),
      assists: stat.assists.toFixed(1),
      turnovers: stat.turnovers.toFixed(1),
      steals: stat.steals.toFixed(1),
      blocks: stat.blocks.toFixed(1)
    }));

    return NextResponse.json({
      success: true,
      data: formattedStats
    });
  } catch (error) {
    console.error('Error fetching team stats:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch team stats' },
      { status: 500 }
    );
  }
}