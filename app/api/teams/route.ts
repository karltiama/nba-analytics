import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const conference = searchParams.get('conference');
    const division = searchParams.get('division');
    const limit = parseInt(searchParams.get('limit') || '50');

    // Build where clause
    const where: any = {};
    if (conference) where.conference = conference;
    if (division) where.division = division;

    const teams = await prisma.team.findMany({
      where,
      orderBy: [
        { conference: 'asc' },
        { division: 'asc' },
        { name: 'asc' }
      ],
      take: limit,
      select: {
        id: true,
        name: true,
        abbreviation: true,
        city: true,
        conference: true,
        division: true,
        logoUrl: true,
        createdAt: true
      }
    });

    return NextResponse.json({
      success: true,
      data: teams
    });
  } catch (error) {
    console.error('Error fetching teams:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch teams' },
      { status: 500 }
    );
  }
}