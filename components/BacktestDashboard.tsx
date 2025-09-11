"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, TrendingDown, Target, DollarSign, BarChart3, RefreshCw, Play, Pause, CheckCircle, XCircle } from 'lucide-react';

interface BacktestResult {
  model_name: string;
  accuracy: number;
  win_rate: number;
  roi: number;
  total_bets: number;
  correct_bets: number;
  avg_confidence: number;
  test_period: string;
  total_games: number;
}

interface ModelComparison {
  model: string;
  roi: number;
  winRate: number;
  totalBets: number;
  accuracy: number;
}

const BacktestDashboard: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState<string>('Logistic Regression');
  const [backtestResults, setBacktestResults] = useState<BacktestResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [modelComparisons, setModelComparisons] = useState<ModelComparison[]>([]);

  const availableModels = [
    'Logistic Regression',
    'Random Forest',
    'Gradient Boosting',
    'XGBoost',
    'Extra Trees',
    'SVM',
    'Neural Network',
    'Naive Bayes',
    'Decision Tree',
    'K-Nearest Neighbors'
  ];

  // Mock data for model comparison (you can replace this with real data)
  const mockModelData: ModelComparison[] = [
    { model: 'Logistic Regression', roi: 49.9, winRate: 0.785, totalBets: 600, accuracy: 0.574 },
    { model: 'Random Forest', roi: 42.4, winRate: 0.746, totalBets: 744, accuracy: 0.586 },
    { model: 'Decision Tree', roi: 41.2, winRate: 0.739, totalBets: 714, accuracy: 0.565 },
    { model: 'Extra Trees', roi: 35.9, winRate: 0.712, totalBets: 896, accuracy: 0.572 },
    { model: 'XGBoost', roi: 25.9, winRate: 0.660, totalBets: 1128, accuracy: 0.580 },
    { model: 'Gradient Boosting', roi: 24.2, winRate: 0.651, totalBets: 1274, accuracy: 0.582 },
    { model: 'SVM', roi: 16.7, winRate: 0.612, totalBets: 834, accuracy: 0.577 },
    { model: 'Naive Bayes', roi: 13.8, winRate: 0.596, totalBets: 1927, accuracy: 0.571 },
    { model: 'Neural Network', roi: 11.6, winRate: 0.584, totalBets: 2026, accuracy: 0.560 },
    { model: 'K-Nearest Neighbors', roi: 10.7, winRate: 0.580, totalBets: 2096, accuracy: 0.556 }
  ];

  useEffect(() => {
    setModelComparisons(mockModelData);
  }, []);

  const runBacktest = async () => {
    setIsLoading(true);
    setIsRunning(true);
    
    try {
      const response = await fetch('/api/backtest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ model_type: selectedModel.toLowerCase().replace(' ', '_').replace('-', '_') }),
      });

      if (!response.ok) {
        throw new Error('Failed to run backtest');
      }

      const data = await response.json();
      setBacktestResults(data);
    } catch (error) {
      console.error('Error running backtest:', error);
      // Don't set mock data, let the user see the error
      alert('Failed to run backtest. Please check the console for details.');
    } finally {
      setIsLoading(false);
      setIsRunning(false);
    }
  };

  const getROIColor = (roi: number) => {
    if (roi >= 40) return 'text-green-600';
    if (roi >= 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getROIBadgeVariant = (roi: number) => {
    if (roi >= 40) return 'success';
    if (roi >= 20) return 'warning';
    return 'destructive';
  };

  const confidenceThresholds = [
    { threshold: 0.5, bets: 1262, winRate: 0.651, roi: 24.2 },
    { threshold: 0.55, bets: 805, winRate: 0.732, roi: 39.7 },
    { threshold: 0.6, bets: 600, winRate: 0.785, roi: 49.9 },
    { threshold: 0.65, bets: 509, winRate: 0.809, roi: 54.5 },
    { threshold: 0.7, bets: 423, winRate: 0.827, roi: 58.0 },
    { threshold: 0.75, bets: 338, winRate: 0.858, roi: 63.8 },
    { threshold: 0.8, bets: 250, winRate: 0.872, roi: 66.5 }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">NBA Betting Model Dashboard</h1>
            <p className="text-gray-600 mt-2">Advanced ML models for NBA spread betting predictions</p>
          </div>
          <div className="flex items-center space-x-4">
            <Select value={selectedModel} onValueChange={setSelectedModel}>
              <SelectTrigger className="w-64">
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                {availableModels.map((model) => (
                  <SelectItem key={model} value={model}>
                    {model}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button 
              onClick={runBacktest} 
              disabled={isLoading}
              className="flex items-center space-x-2"
            >
              {isRunning ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <Play className="h-4 w-4" />
              )}
              <span>{isLoading ? 'Running...' : 'Run Backtest'}</span>
            </Button>
          </div>
        </div>

        {/* Model Comparison Overview */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>Model Performance Comparison</span>
            </CardTitle>
            <CardDescription>
              Compare all trained models by ROI, win rate, and total bets
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {modelComparisons.slice(0, 6).map((model, index) => (
                <Card key={model.model} className="p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-sm">{model.model}</h3>
                    <Badge variant={getROIBadgeVariant(model.roi)}>
                      {model.roi.toFixed(1)}% ROI
                    </Badge>
                  </div>
                  <div className="space-y-1 text-sm text-gray-600">
                    <div className="flex justify-between">
                      <span>Win Rate:</span>
                      <span className="font-medium">{(model.winRate * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Total Bets:</span>
                      <span className="font-medium">{model.totalBets}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Accuracy:</span>
                      <span className="font-medium">{(model.accuracy * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Main Results */}
        {backtestResults && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Key Metrics */}
            <div className="lg:col-span-2 space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Target className="h-5 w-5" />
                    <span>Backtest Results - {backtestResults.model_name}</span>
                  </CardTitle>
                  <CardDescription>
                    Test Period: {backtestResults.test_period}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {backtestResults.roi.toFixed(1)}%
                      </div>
                      <div className="text-sm text-green-700">ROI</div>
                    </div>
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {(backtestResults.win_rate * 100).toFixed(1)}%
                      </div>
                      <div className="text-sm text-blue-700">Win Rate</div>
                    </div>
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">
                        {backtestResults.total_bets}
                      </div>
                      <div className="text-sm text-purple-700">Total Bets</div>
                    </div>
                    <div className="text-center p-4 bg-orange-50 rounded-lg">
                      <div className="text-2xl font-bold text-orange-600">
                        {(backtestResults.accuracy * 100).toFixed(1)}%
                      </div>
                      <div className="text-sm text-orange-700">Accuracy</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Confidence Threshold Analysis */}
              <Card>
                <CardHeader>
                  <CardTitle>Confidence Threshold Analysis</CardTitle>
                  <CardDescription>
                    Performance at different confidence levels
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={confidenceThresholds}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="threshold" 
                        label={{ value: 'Confidence Threshold', position: 'insideBottom', offset: -10 }}
                      />
                      <YAxis 
                        yAxisId="left"
                        label={{ value: 'ROI (%)', angle: -90, position: 'insideLeft' }}
                      />
                      <YAxis 
                        yAxisId="right" 
                        orientation="right"
                        label={{ value: 'Win Rate (%)', angle: 90, position: 'insideRight' }}
                      />
                      <Tooltip 
                        formatter={(value, name) => [
                          name === 'roi' ? `${value}%` : `${(value * 100).toFixed(1)}%`,
                          name === 'roi' ? 'ROI' : 'Win Rate'
                        ]}
                      />
                      <Line 
                        yAxisId="left"
                        type="monotone" 
                        dataKey="roi" 
                        stroke="#10b981" 
                        strokeWidth={2}
                        name="roi"
                      />
                      <Line 
                        yAxisId="right"
                        type="monotone" 
                        dataKey="winRate" 
                        stroke="#3b82f6" 
                        strokeWidth={2}
                        name="winRate"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Model Performance Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Model ROI Comparison</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={modelComparisons.slice(0, 5)} layout="horizontal">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="model" type="category" width={100} />
                      <Tooltip formatter={(value) => [`${value}%`, 'ROI']} />
                      <Bar dataKey="roi" fill="#10b981" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Betting Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle>Betting Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Correct Bets</span>
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <span className="font-medium">{backtestResults.correct_bets}</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Incorrect Bets</span>
                      <div className="flex items-center space-x-2">
                        <XCircle className="h-4 w-4 text-red-500" />
                        <span className="font-medium">{backtestResults.total_bets - backtestResults.correct_bets}</span>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full" 
                        style={{ width: `${(backtestResults.correct_bets / backtestResults.total_bets) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Quick Stats */}
              <Card>
                <CardHeader>
                  <CardTitle>Quick Stats</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Avg Confidence</span>
                    <span className="font-medium">{(backtestResults.avg_confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Test Games</span>
                    <span className="font-medium">{backtestResults.total_games}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Bet Rate</span>
                    <span className="font-medium">
                      {((backtestResults.total_bets / backtestResults.total_games) * 100).toFixed(1)}%
                    </span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Model Details Table */}
        <Card>
          <CardHeader>
            <CardTitle>All Models Performance</CardTitle>
            <CardDescription>
              Complete comparison of all trained models
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4">Model</th>
                    <th className="text-right py-3 px-4">ROI</th>
                    <th className="text-right py-3 px-4">Win Rate</th>
                    <th className="text-right py-3 px-4">Accuracy</th>
                    <th className="text-right py-3 px-4">Total Bets</th>
                    <th className="text-right py-3 px-4">Performance</th>
                  </tr>
                </thead>
                <tbody>
                  {modelComparisons.map((model, index) => (
                    <tr key={model.model} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium">{model.model}</td>
                      <td className="text-right py-3 px-4">
                        <span className={getROIColor(model.roi)}>
                          {model.roi.toFixed(1)}%
                        </span>
                      </td>
                      <td className="text-right py-3 px-4">{(model.winRate * 100).toFixed(1)}%</td>
                      <td className="text-right py-3 px-4">{(model.accuracy * 100).toFixed(1)}%</td>
                      <td className="text-right py-3 px-4">{model.totalBets}</td>
                      <td className="text-right py-3 px-4">
                        <Badge variant={getROIBadgeVariant(model.roi)}>
                          {index < 3 ? 'Top 3' : index < 6 ? 'Good' : 'Fair'}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default BacktestDashboard;
