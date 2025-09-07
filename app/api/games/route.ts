import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const season = searchParams.get('season');
    const seasonType = searchParams.get('seasonType');
    const limit = parseInt(searchParams.get('limit') || '100');
    const includeStats = searchParams.get('includeStats') === 'true';

    // Build where clause
    const where: any = {};
    if (season) where.season = season;
    if (seasonType) where.seasonType = seasonType;

    const games = await prisma.game.findMany({
      where,
      orderBy: { gameDate: 'desc' },
      take: limit,
      include: {
        homeTeam: {
          select: {
            id: true,
            name: true,
            abbreviation: true,
            city: true
          }
        },
        awayTeam: {
          select: {
            id: true,
            name: true,
            abbreviation: true,
            city: true
          }
        }
      }
    });

    // Format the response
    const formattedGames = games.map(game => ({
      id: game.id,
      gameDate: game.gameDate,
      season: game.season,
      seasonType: game.seasonType,
      homeTeam: {
        id: game.homeTeam.id,
        name: game.homeTeam.name,
        abbreviation: game.homeTeam.abbreviation,
        city: game.homeTeam.city
      },
      awayTeam: {
        id: game.awayTeam.id,
        name: game.awayTeam.name,
        abbreviation: game.awayTeam.abbreviation,
        city: game.awayTeam.city
      },
      homeScore: game.homeScore,
      awayScore: game.awayScore,
      status: game.status,
      attendance: game.attendance,
      venue: game.venue
    }));

    return NextResponse.json({
      success: true,
      data: formattedGames
    });
  } catch (error) {
    console.error('Error fetching games:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch games' },
      { status: 500 }
    );
  }
}
