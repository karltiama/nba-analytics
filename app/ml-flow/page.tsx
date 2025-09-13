'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import MLFlowVisualization from '@/components/MLFlowVisualization';
import FeatureImportanceVisualization from '@/components/FeatureImportanceVisualization';
import DecisionTreeVisualization from '@/components/DecisionTreeVisualization';

interface GameData {
  game_id: string;
  game_date: string;
  home_team_abbr: string;
  away_team_abbr: string;
  spread: number;
  total: number;
  home_win_rate: number;
  away_win_rate: number;
  home_point_differential: number;
  away_point_differential: number;
  home_recent_form_5: number;
  away_recent_form_5: number;
  home_rest_days: number;
  away_rest_days: number;
  h2h_games: number;
  h2h_home_wins: number;
  h2h_away_wins: number;
  season_progress: number;
  is_playoffs: boolean;
  is_regular_season: boolean;
}

interface Prediction {
  prediction: number;
  confidence: number;
  probability: number[];
  model_name: string;
  features_used: string[];
  betting_recommendation: string;
}

export default function MLFlowPage() {
  const [games, setGames] = useState<GameData[]>([]);
  const [selectedGame, setSelectedGame] = useState<GameData | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('Random Forest');
  const [activeTab, setActiveTab] = useState<'flow' | 'features' | 'tree'>('flow');

  // Sample game data for demonstration
  const sampleGames: GameData[] = [
    {
      game_id: '1',
      game_date: '2024-01-15',
      home_team_abbr: 'LAL',
      away_team_abbr: 'GSW',
      spread: -3.5,
      total: 230.5,
      home_win_rate: 0.65,
      away_win_rate: 0.58,
      home_point_differential: 4.2,
      away_point_differential: 2.1,
      home_recent_form_5: 0.8,
      away_recent_form_5: 0.6,
      home_rest_days: 2,
      away_rest_days: 1,
      h2h_games: 3,
      h2h_home_wins: 2,
      h2h_away_wins: 1,
      season_progress: 0.6,
      is_playoffs: false,
      is_regular_season: true
    },
    {
      game_id: '2',
      game_date: '2024-01-16',
      home_team_abbr: 'BOS',
      away_team_abbr: 'MIA',
      spread: -7.0,
      total: 215.5,
      home_win_rate: 0.72,
      away_win_rate: 0.45,
      home_point_differential: 8.5,
      away_point_differential: -2.3,
      home_recent_form_5: 0.9,
      away_recent_form_5: 0.4,
      home_rest_days: 3,
      away_rest_days: 0,
      h2h_games: 2,
      h2h_home_wins: 1,
      h2h_away_wins: 1,
      season_progress: 0.6,
      is_playoffs: false,
      is_regular_season: true
    },
    {
      game_id: '3',
      game_date: '2024-01-17',
      home_team_abbr: 'DEN',
      away_team_abbr: 'PHX',
      spread: -2.5,
      total: 225.0,
      home_win_rate: 0.68,
      away_win_rate: 0.62,
      home_point_differential: 5.8,
      away_point_differential: 3.2,
      home_recent_form_5: 0.7,
      away_recent_form_5: 0.8,
      home_rest_days: 1,
      away_rest_days: 2,
      h2h_games: 4,
      h2h_home_wins: 2,
      h2h_away_wins: 2,
      season_progress: 0.6,
      is_playoffs: false,
      is_regular_season: true
    }
  ];

  useEffect(() => {
    setGames(sampleGames);
    setSelectedGame(sampleGames[0]);
  }, []);

  const generatePrediction = async (game: GameData, modelName: string) => {
    setLoading(true);
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Generate mock prediction based on game data
    const mockPrediction: Prediction = {
      prediction: Math.random() > 0.5 ? 1 : 0, // 1 = home wins, 0 = away wins
      confidence: Math.random() * 0.4 + 0.6, // 0.6 to 1.0
      probability: [Math.random() * 0.4 + 0.1, Math.random() * 0.4 + 0.5],
      model_name: modelName,
      features_used: [
        'spread', 'home_win_rate', 'away_win_rate', 'home_point_differential',
        'away_point_differential', 'home_recent_form_5', 'away_recent_form_5'
      ],
      betting_recommendation: `Bet ${game.home_team_abbr} ${game.spread} (${Math.round(Math.random() * 40 + 60)}% confidence)`
    };
    
    setPrediction(mockPrediction);
    setLoading(false);
  };

  const handleGameSelect = (game: GameData) => {
    setSelectedGame(game);
    setPrediction(null);
  };

  const handleModelSelect = (model: string) => {
    setSelectedModel(model);
    setPrediction(null);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold">🤖 ML Model Flow Visualization</h1>
        <p className="text-xl text-muted-foreground">
          See exactly how machine learning models make NBA betting predictions
        </p>
        <Badge variant="outline" className="text-sm">
          Educational Tool for Understanding ML
        </Badge>
      </div>

      {/* Game Selection */}
      <Card>
        <CardHeader>
          <CardTitle>🎮 Select a Game to Analyze</CardTitle>
          <p className="text-sm text-muted-foreground">
            Choose a game to see how different ML models would predict the outcome
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {games.map((game) => (
              <Card 
                key={game.game_id}
                className={`cursor-pointer transition-all ${
                  selectedGame?.game_id === game.game_id 
                    ? 'ring-2 ring-blue-500 bg-blue-50' 
                    : 'hover:bg-gray-50'
                }`}
                onClick={() => handleGameSelect(game)}
              >
                <CardContent className="p-4">
                  <div className="text-center">
                    <div className="font-semibold text-lg">
                      {game.away_team_abbr} @ {game.home_team_abbr}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {game.game_date}
                    </div>
                    <div className="text-sm font-mono">
                      {game.home_team_abbr} {game.spread > 0 ? '+' : ''}{game.spread}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      O/U {game.total}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Model Selection and Prediction */}
      {selectedGame && (
        <Card>
          <CardHeader>
            <CardTitle>🎯 Generate Prediction</CardTitle>
            <p className="text-sm text-muted-foreground">
              Select a model and generate a prediction to see the ML flow
            </p>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 items-center">
              <select 
                value={selectedModel}
                onChange={(e) => handleModelSelect(e.target.value)}
                className="px-3 py-2 border rounded-md"
              >
                <option value="Random Forest">Random Forest</option>
                <option value="Extra Trees">Extra Trees</option>
                <option value="Decision Tree">Decision Tree</option>
                <option value="XGBoost">XGBoost</option>
                <option value="SVM">SVM</option>
                <option value="Neural Network">Neural Network</option>
                <option value="Logistic Regression">Logistic Regression</option>
              </select>
              <Button 
                onClick={() => generatePrediction(selectedGame, selectedModel)}
                disabled={loading}
                className="min-w-32"
              >
                {loading ? 'Generating...' : 'Generate Prediction'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tab Navigation */}
      <Card>
        <CardContent className="p-0">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('flow')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'flow'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              🔄 Prediction Flow
            </button>
            <button
              onClick={() => setActiveTab('features')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'features'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              📊 Feature Importance
            </button>
            <button
              onClick={() => setActiveTab('tree')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'tree'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              🌳 Decision Tree
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Tab Content */}
      {activeTab === 'flow' && selectedGame && prediction && (
        <MLFlowVisualization 
          gameData={selectedGame}
          prediction={prediction}
          modelName={selectedModel}
        />
      )}

      {activeTab === 'features' && (
        <FeatureImportanceVisualization />
      )}

      {activeTab === 'tree' && (
        <DecisionTreeVisualization 
          modelName={selectedModel}
          gameData={selectedGame}
        />
      )}

      {/* Show message if no prediction generated yet */}
      {activeTab === 'flow' && (!selectedGame || !prediction) && (
        <Card>
          <CardContent className="text-center py-12">
            <div className="text-6xl mb-4">🤖</div>
            <h3 className="text-xl font-semibold mb-2">Generate a Prediction First</h3>
            <p className="text-gray-600 mb-4">
              Select a game and generate a prediction to see the ML flow visualization
            </p>
            <Button 
              onClick={() => selectedGame && generatePrediction(selectedGame, selectedModel)}
              disabled={!selectedGame || loading}
            >
              {loading ? 'Generating...' : 'Generate Prediction'}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Educational Content */}
      <Card>
        <CardHeader>
          <CardTitle>🎓 Why This Visualization Matters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="font-semibold text-green-600">✅ Benefits for Learning:</h3>
              <ul className="space-y-2 text-sm">
                <li>• <strong>Transparency:</strong> See exactly how models make decisions</li>
                <li>• <strong>Feature Understanding:</strong> Learn which data points matter most</li>
                <li>• <strong>Model Comparison:</strong> Understand different ML approaches</li>
                <li>• <strong>Confidence Analysis:</strong> Learn to interpret prediction confidence</li>
                <li>• <strong>Debugging:</strong> Identify when models might be wrong</li>
              </ul>
            </div>
            <div className="space-y-4">
              <h3 className="font-semibold text-blue-600">🧠 Key ML Concepts:</h3>
              <ul className="space-y-2 text-sm">
                <li>• <strong>Feature Engineering:</strong> Transforming raw data into useful features</li>
                <li>• <strong>Model Training:</strong> How algorithms learn from historical data</li>
                <li>• <strong>Ensemble Methods:</strong> Combining multiple models for better predictions</li>
                <li>• <strong>Overfitting:</strong> When models memorize training data too well</li>
                <li>• <strong>Cross-Validation:</strong> Testing models on unseen data</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
