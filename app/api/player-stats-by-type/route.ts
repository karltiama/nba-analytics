import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const season = searchParams.get('season');
    const seasonType = searchParams.get('seasonType');
    const teamId = searchParams.get('teamId');
    const limit = parseInt(searchParams.get('limit') || '100');
    const sortBy = searchParams.get('sortBy') || 'pointsPerGame';

    if (!season || !seasonType) {
      return NextResponse.json(
        { success: false, error: 'Season and seasonType are required' },
        { status: 400 }
      );
    }

    // Build where clause
    const where: any = {
      season: season,
      seasonType: seasonType
    };

    if (teamId) {
      where.player = {
        teamId: teamId
      };
    }

    // Build order by clause
    const orderBy: any = {};
    if (sortBy === 'pointsPerGame') orderBy.pointsPerGame = 'desc';
    else if (sortBy === 'rebounds') orderBy.rebounds = 'desc';
    else if (sortBy === 'assists') orderBy.assists = 'desc';
    else if (sortBy === 'gamesPlayed') orderBy.gamesPlayed = 'desc';
    else orderBy.pointsPerGame = 'desc';

    const playerStats = await prisma.playerStats.findMany({
      where,
      orderBy,
      take: limit,
      include: {
        player: {
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
        }
      }
    });

    // Format the response
    const formattedStats = playerStats.map(stat => ({
      id: stat.id,
      season: stat.season,
      seasonType: stat.seasonType,
      player: {
        id: stat.player.id,
        name: stat.player.name,
        position: stat.player.position,
        team: stat.player.team ? {
          id: stat.player.team.id,
          name: stat.player.team.name,
          abbreviation: stat.player.team.abbreviation,
          city: stat.player.team.city,
          conference: stat.player.team.conference,
          division: stat.player.team.division
        } : null
      },
      gamesPlayed: stat.gamesPlayed,
      minutesPerGame: stat.minutesPerGame.toFixed(1),
      pointsPerGame: stat.pointsPerGame.toFixed(1),
      rebounds: stat.rebounds.toFixed(1),
      assists: stat.assists.toFixed(1),
      steals: stat.steals.toFixed(1),
      blocks: stat.blocks.toFixed(1),
      turnovers: stat.turnovers.toFixed(1),
      fieldGoalPct: (stat.fieldGoalPct * 100).toFixed(1),
      threePointPct: (stat.threePointPct * 100).toFixed(1),
      freeThrowPct: (stat.freeThrowPct * 100).toFixed(1)
    }));

    return NextResponse.json({
      success: true,
      data: formattedStats
    });
  } catch (error) {
    console.error('Error fetching player stats by type:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch player stats by type' },
      { status: 500 }
    );
  }
}

