'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ScatterChart, Scatter,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';

interface MLFlowVisualizationProps {
  gameData?: any;
  prediction?: any;
  modelName?: string;
}

interface FeatureImportance {
  feature: string;
  importance: number;
  category: string;
}

interface ModelStep {
  step: string;
  description: string;
  input: any;
  output: any;
  status: 'pending' | 'processing' | 'completed' | 'error';
}

const MLFlowVisualization: React.FC<MLFlowVisualizationProps> = ({ 
  gameData, 
  prediction, 
  modelName = 'Random Forest' 
}) => {
  const [selectedModel, setSelectedModel] = useState(modelName);
  const [activeStep, setActiveStep] = useState(0);
  const [showDetailedFlow, setShowDetailedFlow] = useState(false);

  // Sample feature importance data (in real app, this would come from API)
  const featureImportanceData: FeatureImportance[] = [
    { feature: 'spread', importance: 0.15, category: 'Betting Market' },
    { feature: 'home_win_rate', importance: 0.12, category: 'Team Performance' },
    { feature: 'away_win_rate', importance: 0.11, category: 'Team Performance' },
    { feature: 'home_point_differential', importance: 0.10, category: 'Team Performance' },
    { feature: 'away_point_differential', importance: 0.09, category: 'Team Performance' },
    { feature: 'home_recent_form_5', importance: 0.08, category: 'Recent Form' },
    { feature: 'away_recent_form_5', importance: 0.07, category: 'Recent Form' },
    { feature: 'total', importance: 0.06, category: 'Betting Market' },
    { feature: 'h2h_home_wins', importance: 0.05, category: 'Head-to-Head' },
    { feature: 'rest_days_difference', importance: 0.04, category: 'Scheduling' },
    { feature: 'season_progress', importance: 0.03, category: 'Context' },
    { feature: 'is_playoffs', importance: 0.02, category: 'Context' },
    { feature: 'spread_magnitude', importance: 0.02, category: 'Betting Market' },
    { feature: 'is_home_favorite', importance: 0.01, category: 'Betting Market' },
    { feature: 'favorite_spread', importance: 0.01, category: 'Betting Market' }
  ];

  // Model prediction steps
  const predictionSteps: ModelStep[] = [
    {
      step: 'Data Input',
      description: 'Raw game data and team statistics',
      input: gameData || { home_team: 'Lakers', away_team: 'Warriors', spread: -3.5 },
      output: null,
      status: 'completed'
    },
    {
      step: 'Feature Engineering',
      description: 'Transform raw data into ML features',
      input: 'Raw game data',
      output: '29 engineered features',
      status: 'completed'
    },
    {
      step: 'Feature Scaling',
      description: 'Normalize features using StandardScaler',
      input: '29 raw features',
      output: '29 scaled features',
      status: 'completed'
    },
    {
      step: 'Model Prediction',
      description: `${selectedModel} processes the features`,
      input: '29 scaled features',
      output: prediction || { prediction: 1, confidence: 0.74, probability: [0.26, 0.74] },
      status: 'completed'
    },
    {
      step: 'Confidence Analysis',
      description: 'Analyze prediction confidence and risk',
      input: 'Model probabilities',
      output: 'Confidence score and betting recommendation',
      status: 'completed'
    },
    {
      step: 'Final Output',
      description: 'Generate betting recommendation',
      input: 'All processed data',
      output: 'Bet: Home team -3.5 (74% confidence)',
      status: 'completed'
    }
  ];

  // Model comparison data
  const modelComparisonData = [
    { model: 'Random Forest', accuracy: 57.5, roi: 47.4, winRate: 73.7, bets: 813 },
    { model: 'Extra Trees', accuracy: 58.5, roi: 47.2, winRate: 73.6, bets: 825 },
    { model: 'Decision Tree', accuracy: 54.6, roi: 29.1, winRate: 64.5, bets: 984 },
    { model: 'XGBoost', accuracy: 59.1, roi: 21.9, winRate: 60.9, bets: 1774 },
    { model: 'SVM', accuracy: 57.7, roi: 21.9, winRate: 60.9, bets: 850 },
    { model: 'Neural Network', accuracy: 58.4, roi: 11.6, winRate: 58.4, bets: 1200 },
    { model: 'Logistic Regression', accuracy: 57.4, roi: 49.9, winRate: 78.5, bets: 600 }
  ];

  // Feature categories for radar chart
  const featureCategories = [
    { category: 'Team Performance', value: 0.42, fullMark: 0.5 },
    { category: 'Recent Form', value: 0.15, fullMark: 0.2 },
    { category: 'Betting Market', value: 0.24, fullMark: 0.3 },
    { category: 'Head-to-Head', value: 0.05, fullMark: 0.1 },
    { category: 'Scheduling', value: 0.04, fullMark: 0.1 },
    { category: 'Context', value: 0.05, fullMark: 0.1 }
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🤖 ML Model Flow Visualization
            <Badge variant="secondary">Educational</Badge>
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            See exactly how your machine learning models make predictions step by step
          </p>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 items-center">
            <Select value={selectedModel} onValueChange={setSelectedModel}>
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Random Forest">Random Forest</SelectItem>
                <SelectItem value="Extra Trees">Extra Trees</SelectItem>
                <SelectItem value="Decision Tree">Decision Tree</SelectItem>
                <SelectItem value="XGBoost">XGBoost</SelectItem>
                <SelectItem value="SVM">SVM</SelectItem>
                <SelectItem value="Neural Network">Neural Network</SelectItem>
                <SelectItem value="Logistic Regression">Logistic Regression</SelectItem>
              </SelectContent>
            </Select>
            <Button 
              variant="outline" 
              onClick={() => setShowDetailedFlow(!showDetailedFlow)}
            >
              {showDetailedFlow ? 'Hide' : 'Show'} Detailed Flow
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Prediction Flow Steps */}
      <Card>
        <CardHeader>
          <CardTitle>🔄 Prediction Pipeline</CardTitle>
          <p className="text-sm text-muted-foreground">
            Step-by-step process of how {selectedModel} makes predictions
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {predictionSteps.map((step, index) => (
              <div 
                key={index}
                className={`p-4 rounded-lg border-2 transition-all ${
                  index === activeStep 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-4">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold ${
                    step.status === 'completed' ? 'bg-green-500' : 
                    step.status === 'processing' ? 'bg-blue-500' : 
                    step.status === 'error' ? 'bg-red-500' : 'bg-gray-400'
                  }`}>
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold">{step.step}</h3>
                    <p className="text-sm text-muted-foreground">{step.description}</p>
                    {showDetailedFlow && (
                      <div className="mt-2 text-xs space-y-1">
                        <div><strong>Input:</strong> {JSON.stringify(step.input)}</div>
                        {step.output && (
                          <div><strong>Output:</strong> {JSON.stringify(step.output)}</div>
                        )}
                      </div>
                    )}
                  </div>
                  <Badge variant={step.status === 'completed' ? 'default' : 'secondary'}>
                    {step.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Feature Importance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>📊 Feature Importance</CardTitle>
            <p className="text-sm text-muted-foreground">
              Which features matter most for {selectedModel} predictions
            </p>
          </CardHeader>
          <CardContent>
            <BarChart width={600} height={300} data={featureImportanceData.slice(0, 10)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="feature" 
                angle={-45}
                textAnchor="end"
                height={80}
                fontSize={12}
              />
              <YAxis />
              <Tooltip />
              <Bar dataKey="importance" fill="#8884d8" />
            </BarChart>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>🎯 Feature Categories</CardTitle>
            <p className="text-sm text-muted-foreground">
              How different types of features contribute to predictions
            </p>
          </CardHeader>
          <CardContent>
            <RadarChart width={400} height={300} data={featureCategories}>
              <PolarGrid />
              <PolarAngleAxis dataKey="category" />
              <PolarRadiusAxis angle={90} domain={[0, 0.5]} />
              <Radar 
                name="Importance" 
                dataKey="value" 
                stroke="#8884d8" 
                fill="#8884d8" 
                fillOpacity={0.6} 
              />
            </RadarChart>
          </CardContent>
        </Card>
      </div>

      {/* Model Comparison */}
      <Card>
        <CardHeader>
          <CardTitle>⚖️ Model Performance Comparison</CardTitle>
          <p className="text-sm text-muted-foreground">
            How different models perform on the same data
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-4">ROI vs Win Rate</h4>
              <ScatterChart width={400} height={250} data={modelComparisonData}>
                <CartesianGrid />
                <XAxis dataKey="winRate" name="Win Rate" />
                <YAxis dataKey="roi" name="ROI" />
                <Tooltip />
                <Scatter dataKey="roi" fill="#8884d8" />
              </ScatterChart>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Accuracy vs Total Bets</h4>
              <ScatterChart width={400} height={250} data={modelComparisonData}>
                <CartesianGrid />
                <XAxis dataKey="accuracy" name="Accuracy" />
                <YAxis dataKey="bets" name="Total Bets" />
                <Tooltip />
                <Scatter dataKey="bets" fill="#00C49F" />
              </ScatterChart>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Decision Tree Visualization (for Random Forest) */}
      {selectedModel === 'Random Forest' && (
        <Card>
          <CardHeader>
            <CardTitle>🌳 Random Forest Decision Process</CardTitle>
            <p className="text-sm text-muted-foreground">
              How Random Forest combines multiple decision trees
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 border rounded-lg text-center">
                  <div className="text-2xl font-bold text-blue-600">200</div>
                  <div className="text-sm text-muted-foreground">Decision Trees</div>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <div className="text-2xl font-bold text-green-600">10</div>
                  <div className="text-sm text-muted-foreground">Max Depth</div>
                </div>
                <div className="p-4 border rounded-lg text-center">
                  <div className="text-2xl font-bold text-purple-600">74%</div>
                  <div className="text-sm text-muted-foreground">Avg Confidence</div>
                </div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold mb-2">How Random Forest Works:</h4>
                <ol className="text-sm space-y-1 list-decimal list-inside">
                  <li>Creates 200 different decision trees using random subsets of data</li>
                  <li>Each tree votes on the prediction (Home team wins or Away team wins)</li>
                  <li>Final prediction is the majority vote across all trees</li>
                  <li>Confidence is calculated as the percentage of trees that agree</li>
                  <li>Higher confidence = more trees agreeing = more reliable prediction</li>
                </ol>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Learning Insights */}
      <Card>
        <CardHeader>
          <CardTitle>🎓 Key Learning Points</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h4 className="font-semibold text-green-600">✅ What Makes a Good Feature:</h4>
              <ul className="text-sm space-y-1 list-disc list-inside">
                <li>Team performance metrics (win rate, point differential)</li>
                <li>Recent form and momentum</li>
                <li>Betting market information (spreads, totals)</li>
                <li>Head-to-head history</li>
                <li>Scheduling factors (rest days, travel)</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold text-blue-600">🧠 Model Insights:</h4>
              <ul className="text-sm space-y-1 list-disc list-inside">
                <li>Random Forest works by combining many simple decision trees</li>
                <li>Each tree sees different data, reducing overfitting</li>
                <li>Confidence scores help identify reliable predictions</li>
                <li>Higher confidence doesn't always mean higher accuracy</li>
                <li>Feature importance shows what the model "learned" to focus on</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MLFlowVisualization;
