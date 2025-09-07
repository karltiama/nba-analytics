import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function GET(request: NextRequest) {
  try {
    // Get data quality metrics
    const [teamsCount, gamesCount, teamStatsCount] = await Promise.all([
      prisma.team.count(),
      prisma.game.count(),
      prisma.teamStats.count()
    ]);

    // Get date ranges
    const [earliestGame, latestGame] = await Promise.all([
      prisma.game.findFirst({
        orderBy: { gameDate: 'asc' },
        select: { gameDate: true }
      }),
      prisma.game.findFirst({
        orderBy: { gameDate: 'desc' },
        select: { gameDate: true }
      })
    ]);

    // Get season breakdown
    const seasonBreakdown = await prisma.game.groupBy({
      by: ['season', 'seasonType'],
      _count: { id: true },
      orderBy: { season: 'desc' }
    });

    // Get teams by conference
    const teamsByConference = await prisma.team.groupBy({
      by: ['conference'],
      _count: { id: true }
    });

    return NextResponse.json({
      success: true,
      data: {
        summary: {
          teamsCount,
          gamesCount,
          teamStatsCount,
          dateRange: {
            earliest: earliestGame?.gameDate,
            latest: latestGame?.gameDate
          }
        },
        seasonBreakdown: seasonBreakdown.map(s => ({
          season: s.season,
          seasonType: s.seasonType,
          gameCount: s._count.id
        })),
        teamsByConference: teamsByConference.map(t => ({
          conference: t.conference,
          teamCount: t._count.id
        }))
      }
    });
  } catch (error) {
    console.error('Error fetching data quality metrics:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch data quality metrics' },
      { status: 500 }
    );
  }
}
