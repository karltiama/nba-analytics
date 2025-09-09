import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// Python ML service URL
const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:8000';

async function callMLService(endpoint: string, data?: any) {
  try {
    const url = `${ML_SERVICE_URL}${endpoint}`;
    const options: RequestInit = {
      method: data ? 'POST' : 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    };
    
    if (data) {
      options.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, options);
    
    if (!response.ok) {
      throw new Error(`ML service error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('ML service call failed:', error);
    throw new Error('ML service unavailable');
  }
}

// GET /api/predictions - Get predictions for upcoming games
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const gameId = searchParams.get('gameId');
    const limit = parseInt(searchParams.get('limit') || '10');
    
    // Get upcoming games
    const whereClause = gameId 
      ? { id: gameId }
      : { 
          gameDate: { gte: new Date() },
          status: { not: 'Final' }
        };
    
    const games = await prisma.game.findMany({
      where: whereClause,
      include: {
        homeTeam: true,
        awayTeam: true,
        predictions: {
          where: { modelName: 'Gradient Boosting' },
          orderBy: { createdAt: 'desc' },
          take: 1
        }
      },
      orderBy: { gameDate: 'asc' },
      take: limit
    });
    
    // Generate predictions for games that don't have them
    const predictions = [];
    
    for (const game of games) {
      if (game.predictions.length === 0) {
        try {
          // Call Python ML service to generate prediction
          const mlResponse = await callMLService(`/predict-game/${game.id}`);
          
          // Save prediction to database
          const savedPrediction = await prisma.prediction.create({
            data: {
              gameId: game.id,
              modelName: 'Gradient Boosting',
              modelVersion: '1.0',
              predictionType: 'spread',
              predictedValue: mlResponse.predicted_class,
              confidence: mlResponse.confidence,
              createdAt: new Date()
            }
          });
          
          predictions.push({
            game,
            prediction: savedPrediction,
            recommendation: mlResponse.recommendation
          });
        } catch (error) {
          console.error(`Failed to predict game ${game.id}:`, error);
          // Skip this game if prediction fails
        }
      } else {
        // Use existing prediction
        const existingPrediction = game.predictions[0];
        predictions.push({
          game,
          prediction: existingPrediction,
          recommendation: {
            shouldBet: existingPrediction.confidence >= 0.5,
            betType: existingPrediction.predictedValue === 1 ? 'Favorite Covers' : 'Underdog Covers',
            confidence: existingPrediction.confidence,
            recommendation: existingPrediction.confidence >= 0.5 
              ? `Bet on ${existingPrediction.predictedValue === 1 ? 'Favorite Covers' : 'Underdog Covers'}`
              : 'No bet - Confidence too low'
          }
        });
      }
    }
    
    return NextResponse.json({
      success: true,
      data: predictions,
      modelInfo: {
        name: 'Gradient Boosting',
        version: '1.0',
        threshold: 0.5
      }
    });
    
  } catch (error) {
    console.error('Prediction error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to generate predictions' },
      { status: 500 }
    );
  }
}

// POST /api/predictions - Create a new prediction
export async function POST(request: NextRequest) {
  try {
    const { gameId } = await request.json();
    
    if (!gameId) {
      return NextResponse.json(
        { success: false, error: 'Game ID is required' },
        { status: 400 }
      );
    }
    
    // Get game data
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
    
    // Call Python ML service to generate prediction
    const mlResponse = await callMLService(`/predict-game/${gameId}`);
    
    // Save prediction
    const savedPrediction = await prisma.prediction.create({
      data: {
        gameId: game.id,
        modelName: 'Gradient Boosting',
        modelVersion: '1.0',
        predictionType: 'spread',
        predictedValue: mlResponse.predicted_class,
        confidence: mlResponse.confidence,
        createdAt: new Date()
      }
    });
    
    return NextResponse.json({
      success: true,
      data: {
        game,
        prediction: savedPrediction,
        recommendation: mlResponse.recommendation
      }
    });
    
  } catch (error) {
    console.error('Prediction creation error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to create prediction' },
      { status: 500 }
    );
  }
}