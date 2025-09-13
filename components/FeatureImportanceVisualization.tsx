'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  PieChart, Pie, Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ScatterChart, Scatter
} from 'recharts';

interface FeatureImportanceData {
  feature: string;
  importance: number;
  category: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
}

interface ModelComparison {
  model: string;
  topFeatures: string[];
  featureCount: number;
  accuracy: number;
  roi: number;
}

const FeatureImportanceVisualization: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState('Random Forest');
  const [viewType, setViewType] = useState<'bar' | 'pie' | 'radar' | 'scatter'>('bar');

  // Comprehensive feature importance data
  const featureData: FeatureImportanceData[] = [
    { feature: 'spread', importance: 0.15, category: 'Betting Market', description: 'Point spread from sportsbooks', impact: 'high' },
    { feature: 'home_win_rate', importance: 0.12, category: 'Team Performance', description: 'Home team win percentage', impact: 'high' },
    { feature: 'away_win_rate', importance: 0.11, category: 'Team Performance', description: 'Away team win percentage', impact: 'high' },
    { feature: 'home_point_differential', importance: 0.10, category: 'Team Performance', description: 'Home team point differential', impact: 'high' },
    { feature: 'away_point_differential', importance: 0.09, category: 'Team Performance', description: 'Away team point differential', impact: 'high' },
    { feature: 'home_recent_form_5', importance: 0.08, category: 'Recent Form', description: 'Home team last 5 games', impact: 'medium' },
    { feature: 'away_recent_form_5', importance: 0.07, category: 'Recent Form', description: 'Away team last 5 games', impact: 'medium' },
    { feature: 'total', importance: 0.06, category: 'Betting Market', description: 'Over/under total points', impact: 'medium' },
    { feature: 'h2h_home_wins', importance: 0.05, category: 'Head-to-Head', description: 'Home team H2H wins', impact: 'medium' },
    { feature: 'rest_days_difference', importance: 0.04, category: 'Scheduling', description: 'Rest advantage difference', impact: 'low' },
    { feature: 'season_progress', importance: 0.03, category: 'Context', description: 'How far into season', impact: 'low' },
    { feature: 'is_playoffs', importance: 0.02, category: 'Context', description: 'Playoff game indicator', impact: 'low' },
    { feature: 'spread_magnitude', importance: 0.02, category: 'Betting Market', description: 'Absolute spread value', impact: 'low' },
    { feature: 'is_home_favorite', importance: 0.01, category: 'Betting Market', description: 'Home team favored', impact: 'low' },
    { feature: 'favorite_spread', importance: 0.01, category: 'Betting Market', description: 'Favorite spread value', impact: 'low' }
  ];

  // Model comparison data
  const modelComparison: ModelComparison[] = [
    { model: 'Random Forest', topFeatures: ['spread', 'home_win_rate', 'away_win_rate'], featureCount: 29, accuracy: 57.5, roi: 47.4 },
    { model: 'Extra Trees', topFeatures: ['spread', 'home_point_differential', 'away_point_differential'], featureCount: 29, accuracy: 58.5, roi: 47.2 },
    { model: 'Decision Tree', topFeatures: ['spread', 'home_win_rate', 'total'], featureCount: 29, accuracy: 54.6, roi: 29.1 },
    { model: 'XGBoost', topFeatures: ['spread', 'home_recent_form_5', 'away_recent_form_5'], featureCount: 29, accuracy: 59.1, roi: 21.9 },
    { model: 'SVM', topFeatures: ['spread', 'home_win_rate', 'away_win_rate'], featureCount: 29, accuracy: 57.7, roi: 21.9 },
    { model: 'Neural Network', topFeatures: ['spread', 'home_point_differential', 'total'], featureCount: 29, accuracy: 58.4, roi: 11.6 }
  ];

  // Category aggregation
  const categoryData = featureData.reduce((acc, feature) => {
    const existing = acc.find(cat => cat.category === feature.category);
    if (existing) {
      existing.importance += feature.importance;
      existing.count += 1;
    } else {
      acc.push({
        category: feature.category,
        importance: feature.importance,
        count: 1,
        color: getCategoryColor(feature.category)
      });
    }
    return acc;
  }, [] as Array<{category: string, importance: number, count: number, color: string}>);

  function getCategoryColor(category: string): string {
    const colors = {
      'Team Performance': '#8884d8',
      'Betting Market': '#82ca9d',
      'Recent Form': '#ffc658',
      'Head-to-Head': '#ff7300',
      'Scheduling': '#00c49f',
      'Context': '#ff6b6b'
    };
    return colors[category as keyof typeof colors] || '#8884d8';
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82ca9d'];

  const topFeatures = featureData.slice(0, 8);
  const highImpactFeatures = featureData.filter(f => f.impact === 'high');

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            📊 Feature Importance Analysis
            <Badge variant="secondary">Educational</Badge>
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Understand which features your ML models rely on most for predictions
          </p>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 items-center">
            <select 
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="px-3 py-2 border rounded-md"
            >
              <option value="Random Forest">Random Forest</option>
              <option value="Extra Trees">Extra Trees</option>
              <option value="Decision Tree">Decision Tree</option>
              <option value="XGBoost">XGBoost</option>
              <option value="SVM">SVM</option>
              <option value="Neural Network">Neural Network</option>
            </select>
            <div className="flex gap-2">
              {(['bar', 'pie', 'radar', 'scatter'] as const).map((type) => (
                <Button
                  key={type}
                  variant={viewType === type ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setViewType(type)}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Visualization */}
      <Card>
        <CardHeader>
          <CardTitle>🎯 Top Features for {selectedModel}</CardTitle>
          <p className="text-sm text-muted-foreground">
            {viewType === 'bar' && 'Bar chart showing feature importance values'}
            {viewType === 'pie' && 'Pie chart showing relative feature importance'}
            {viewType === 'radar' && 'Radar chart showing feature categories'}
            {viewType === 'scatter' && 'Scatter plot comparing feature importance vs impact'}
          </p>
        </CardHeader>
        <CardContent>
          <div className="h-96">
            {viewType === 'bar' && (
              <BarChart width={800} height={350} data={topFeatures} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 0.2]} />
                <YAxis dataKey="feature" type="category" width={120} />
                <Tooltip 
                  formatter={(value: number) => [value.toFixed(3), 'Importance']}
                  labelFormatter={(label) => `Feature: ${label}`}
                />
                <Bar dataKey="importance" fill="#8884d8" />
              </BarChart>
            )}
            
            {viewType === 'pie' && (
              <PieChart width={400} height={350}>
                <Pie
                  data={topFeatures}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ feature, importance }) => `${feature}: ${(importance * 100).toFixed(1)}%`}
                  outerRadius={120}
                  fill="#8884d8"
                  dataKey="importance"
                >
                  {topFeatures.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => [value.toFixed(3), 'Importance']} />
              </PieChart>
            )}
            
            {viewType === 'radar' && (
              <RadarChart width={400} height={350} data={categoryData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="category" />
                <PolarRadiusAxis angle={90} domain={[0, 0.5]} />
                <Radar
                  name="Importance"
                  dataKey="importance"
                  stroke="#8884d8"
                  fill="#8884d8"
                  fillOpacity={0.6}
                />
              </RadarChart>
            )}
            
            {viewType === 'scatter' && (
              <ScatterChart width={400} height={350} data={featureData}>
                <CartesianGrid />
                <XAxis dataKey="importance" name="Importance" />
                <YAxis dataKey="impact" name="Impact" />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  formatter={(value: number, name: string) => [value, name]}
                  labelFormatter={(label, payload) => 
                    payload && payload[0] ? `Feature: ${payload[0].payload.feature}` : ''
                  }
                />
                <Scatter 
                  dataKey="importance" 
                  fill="#8884d8"
                  shape="circle"
                  r={6}
                />
              </ScatterChart>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Feature Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>🔥 High Impact Features</CardTitle>
            <p className="text-sm text-muted-foreground">
              Features that have the strongest influence on predictions
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {highImpactFeatures.map((feature, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div>
                    <div className="font-semibold text-green-800">{feature.feature}</div>
                    <div className="text-sm text-green-600">{feature.description}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-green-800">{(feature.importance * 100).toFixed(1)}%</div>
                    <Badge variant="secondary" className="text-xs">
                      {feature.category}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>📈 Feature Categories</CardTitle>
            <p className="text-sm text-muted-foreground">
              How different types of features contribute to predictions
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {categoryData.map((category, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: category.color }}
                    />
                    <span className="font-medium">{category.category}</span>
                    <Badge variant="outline" className="text-xs">
                      {category.count} features
                    </Badge>
                  </div>
                  <div className="text-right">
                    <div className="font-bold">{(category.importance * 100).toFixed(1)}%</div>
                    <div className="text-xs text-muted-foreground">total importance</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Model Comparison */}
      <Card>
        <CardHeader>
          <CardTitle>⚖️ Model Feature Usage Comparison</CardTitle>
          <p className="text-sm text-muted-foreground">
            How different models prioritize different features
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {modelComparison.map((model, index) => (
              <div key={index} className="p-4 border rounded-lg">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold">{model.model}</h3>
                  <div className="text-right text-sm text-muted-foreground">
                    {model.featureCount} features | {model.accuracy}% accuracy | {model.roi}% ROI
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  {model.topFeatures.map((feature, idx) => (
                    <Badge key={idx} variant="secondary" className="text-xs">
                      {feature}
                    </Badge>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Learning Insights */}
      <Card>
        <CardHeader>
          <CardTitle>🎓 Key Insights About Feature Importance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-semibold text-green-600">✅ What Makes Features Important:</h4>
              <ul className="text-sm space-y-1 list-disc list-inside">
                <li><strong>Predictive Power:</strong> Features that consistently correlate with outcomes</li>
                <li><strong>Information Content:</strong> Features that reduce uncertainty</li>
                <li><strong>Stability:</strong> Features that work across different game situations</li>
                <li><strong>Independence:</strong> Features that don't duplicate other information</li>
                <li><strong>Data Quality:</strong> Features with clean, reliable data</li>
              </ul>
            </div>
            <div className="space-y-3">
              <h4 className="font-semibold text-blue-600">🧠 Model-Specific Insights:</h4>
              <ul className="text-sm space-y-1 list-disc list-inside">
                <li><strong>Tree Models:</strong> Focus on features that create clear decision boundaries</li>
                <li><strong>Linear Models:</strong> Weight features based on correlation strength</li>
                <li><strong>Ensemble Models:</strong> Combine multiple feature perspectives</li>
                <li><strong>Neural Networks:</strong> Learn complex feature interactions</li>
                <li><strong>Feature Selection:</strong> Some models automatically ignore less useful features</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default FeatureImportanceVisualization;
