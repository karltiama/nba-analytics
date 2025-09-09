import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// GET /api/bets - Get user's betting history
export async function GET(request: NextRequest) {
  try {
    const bets = await prisma.userBet.findMany({
      include: {
        game: {
          include: {
            homeTeam: true,
            awayTeam: true
          }
        }
      },
      orderBy: { createdAt: 'desc' }
    });

    return NextResponse.json({
      success: true,
      data: bets
    });
    
  } catch (error) {
    console.error('Error fetching bets:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch betting history' },
      { status: 500 }
    );
  }
}

// POST /api/bets - Place a new bet
export async function POST(request: NextRequest) {
  try {
    const { gameId, betType, betAmount, betSide, odds } = await request.json();
    
    if (!gameId || !betType || !betAmount || !betSide) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields' },
        { status: 400 }
      );
    }
    
    // Get game details
    const game = await prisma.game.findUnique({
      where: { id: gameId },
      include: {
        homeTeam: true,
        awayTeam: true
      }
    });
    
    if (!game) {
      return NextResponse.json(
        { success: false, error: 'Game not found' },
        { status: 404 }
      );
    }
    
    // Calculate potential win
    const standardOdds = odds || -110;
    const potentialWin = Math.round((betAmount * 100) / Math.abs(standardOdds));
    
    // Create the bet
    const bet = await prisma.userBet.create({
      data: {
        gameId: gameId,
        betType: betType,
        betAmount: betAmount,
        odds: standardOdds,
        potentialWin: potentialWin,
        status: 'pending'
      },
      include: {
        game: {
          include: {
            homeTeam: true,
            awayTeam: true
          }
        }
      }
    });
    
    return NextResponse.json({
      success: true,
      data: bet,
      message: 'Bet placed successfully'
    });
    
  } catch (error) {
    console.error('Error placing bet:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to place bet' },
      { status: 500 }
    );
  }
}

// PUT /api/bets - Update bet status (for when games are completed)
export async function PUT(request: NextRequest) {
  try {
    const { betId, status, actualWin } = await request.json();
    
    if (!betId || !status) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields' },
        { status: 400 }
      );
    }
    
    const bet = await prisma.userBet.update({
      where: { id: betId },
      data: {
        status: status,
        actualWin: actualWin || null
      }
    });
    
    return NextResponse.json({
      success: true,
      data: bet,
      message: 'Bet updated successfully'
    });
    
  } catch (error) {
    console.error('Error updating bet:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to update bet' },
      { status: 500 }
    );
  }
}
