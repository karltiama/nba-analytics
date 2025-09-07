import { NextResponse } from 'next/server'
import { prisma } from '@/lib/database'

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const season = searchParams.get('season') || '2023-24'
    const limit = parseInt(searchParams.get('limit') || '50')
    const sortBy = searchParams.get('sortBy') || 'pointsPerGame'
    const sortOrder = searchParams.get('sortOrder') || 'desc'
    const position = searchParams.get('position') // Filter by position if provided

    const whereClause: any = {
      season: season
    }

    if (position) {
      whereClause.player = {
        position: position
      }
    }

    const playerStats = await prisma.playerStats.findMany({
      where: whereClause,
      include: {
        player: {
          include: {
            team: true
          }
        }
      },
      orderBy: {
        [sortBy]: sortOrder as 'asc' | 'desc'
      },
      take: limit
    })

    return NextResponse.json({ success: true, data: playerStats })
  } catch (error) {
    console.error('Error fetching player stats:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to fetch player stats' },
      { status: 500 }
    )
  }
}


