'use client';

import { useState } from 'react';

interface BacktestResult {
  accuracy: number;
  win_rate: number;
  roi: number;
  total_bets: number;
  correct_bets: number;
  avg_confidence: number;
  season_performance: Record<string, {
    total_bets: number;
    correct_bets: number;
    win_rate: number;
    roi: number;
  }>;
  sample_predictions: Array<{
    game: string;
    date: string;
    spread: number;
    predicted: string;
    actual: string;
    correct: boolean;
    confidence: number;
  }>;
  error?: string;
  missing_files?: string[];
  message?: string;
}

export default function BacktestPage() {
  const [results, setResults] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedModel, setSelectedModel] = useState('advanced');
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.6);

  const runBacktest = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/backtest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          season_start: '2020-21',
          season_end: '2024-25',
          confidence_threshold: confidenceThreshold,
          model_type: selectedModel
        })
      });

      if (!response.ok) {
        throw new Error('Failed to run backtest');
      }

      const data = await response.json();
      
      // Check if there's an error in the response
      if (data.error) {
        setError(data.error + (data.details ? ': ' + data.details : ''));
        // Still show results if they exist (for mock data)
        if (data.accuracy !== undefined) {
          setResults(data);
        }
      } else {
        setResults(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getPerformanceColor = (roi: number) => {
    if (roi > 5) return 'text-green-600';
    if (roi > 0) return 'text-green-500';
    if (roi > -5) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getPerformanceBadge = (roi: number) => {
    if (roi > 5) return 'bg-green-100 text-green-800 px-2 py-1 rounded text-sm';
    if (roi > 0) return 'bg-green-100 text-green-800 px-2 py-1 rounded text-sm';
    if (roi > -5) return 'bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-sm';
    return 'bg-red-100 text-red-800 px-2 py-1 rounded text-sm';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Model Backtest Results</h1>
            <p className="text-gray-600 mt-2">
              Test your NBA betting model on historical data
            </p>
          </div>
          <div className="flex items-center gap-4">
            {/* Model Selection */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-gray-700">Model Type</label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="basic">Basic Model</option>
                <option value="advanced">Advanced Model</option>
                <option value="xgboost">XGBoost Model</option>
              </select>
            </div>

            {/* Confidence Threshold */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-gray-700">Confidence Threshold</label>
              <select
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={0.5}>0.5 (All Predictions)</option>
                <option value={0.55}>0.55 (High Confidence)</option>
                <option value={0.6}>0.6 (Very High Confidence)</option>
                <option value={0.65}>0.65 (Extreme Confidence)</option>
                <option value={0.7}>0.7 (Maximum Confidence)</option>
              </select>
            </div>

            <button 
              onClick={runBacktest} 
              disabled={loading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Running Backtest...
                </>
              ) : (
                <>
                  <span>📊</span>
                  Run Backtest
                </>
              )}
            </button>

            <a
              href="/backtest/compare"
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 flex items-center gap-2"
            >
              <span>⚖️</span>
              Compare Models
            </a>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2 text-red-600">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          </div>
        )}

        {/* Missing Files Warning */}
        {results?.missing_files && results.missing_files.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <div className="flex items-start gap-2 text-yellow-800">
              <span>📁</span>
              <div>
                <div className="font-medium">Missing Required Files:</div>
                <ul className="list-disc list-inside mt-2 text-sm">
                  {results.missing_files.map((file, index) => (
                    <li key={index}>{file}</li>
                  ))}
                </ul>
                <div className="mt-2 text-sm">
                  <strong>Solution:</strong> Run the ML model training scripts first:
                  <div className="mt-1 font-mono text-xs bg-yellow-100 p-2 rounded">
                    python create_advanced_ml_models.py
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="space-y-6">
            {/* Tabs */}
            <div className="border-b border-gray-200">
              <nav className="flex space-x-8">
                <button
                  onClick={() => setActiveTab('overview')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'overview'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Overview
                </button>
                <button
                  onClick={() => setActiveTab('seasons')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'seasons'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Season Breakdown
                </button>
                <button
                  onClick={() => setActiveTab('predictions')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'predictions'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Sample Predictions
                </button>
              </nav>
            </div>

            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Overall Accuracy</p>
                        <p className="text-2xl font-bold text-gray-900">{results.accuracy?.toFixed(3) || 'N/A'}</p>
                        <p className="text-xs text-gray-500">
                          {results.accuracy && results.accuracy > 0.52 ? 'Above baseline' : 'Below baseline'}
                        </p>
                      </div>
                      <span className="text-2xl">🎯</span>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Win Rate</p>
                        <p className="text-2xl font-bold text-gray-900">{results.win_rate?.toFixed(3) || 'N/A'}</p>
                        <p className="text-xs text-gray-500">High-confidence bets only</p>
                      </div>
                      <span className="text-2xl">📈</span>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">ROI</p>
                        <p className={`text-2xl font-bold ${getPerformanceColor(results.roi || 0)}`}>
                          {results.roi?.toFixed(1) || 'N/A'}%
                        </p>
                        <div className="mt-2">
                          <span className={getPerformanceBadge(results.roi || 0)}>
                            {results.roi && results.roi > 5 ? 'Excellent' : results.roi && results.roi > 0 ? 'Profitable' : results.roi && results.roi > -5 ? 'Break-even' : 'Losing'}
                          </span>
                        </div>
                      </div>
                      <span className="text-2xl">💰</span>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Total Bets</p>
                        <p className="text-2xl font-bold text-gray-900">{results.total_bets || 0}</p>
                        <p className="text-xs text-gray-500">
                          {results.correct_bets || 0} correct ({results.win_rate?.toFixed(1) || '0.0'}%)
                        </p>
                      </div>
                      <span className="text-2xl">📊</span>
                    </div>
                  </div>
                </div>

                {/* Performance Summary */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Summary</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div className="flex justify-between">
                        <span className="text-sm font-medium text-gray-600">Average Confidence:</span>
                        <span className="text-sm text-gray-900">{results.avg_confidence?.toFixed(3) || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm font-medium text-gray-600">Confidence Threshold:</span>
                        <span className="text-sm text-gray-900">0.6</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm font-medium text-gray-600">Betting Odds:</span>
                        <span className="text-sm text-gray-900">-110 (Standard)</span>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div className="flex justify-between">
                        <span className="text-sm font-medium text-gray-600">Total Wagered:</span>
                        <span className="text-sm text-gray-900">${((results.total_bets || 0) * 110).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm font-medium text-gray-600">Net Profit:</span>
                        <span className={`text-sm ${getPerformanceColor(results.roi || 0)}`}>
                          ${(((results.total_bets || 0) * 110 * (results.roi || 0)) / 100).toFixed(0)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm font-medium text-gray-600">Sharpe Ratio:</span>
                        <span className="text-sm text-gray-900">N/A</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Seasons Tab */}
            {activeTab === 'seasons' && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Season-by-Season Performance</h3>
                <div className="space-y-4">
                  {results.season_performance && Object.entries(results.season_performance).map(([season, data]) => (
                    <div key={season} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-4">
                        <span className="text-xl">📅</span>
                        <div>
                          <div className="font-medium text-gray-900">{season}</div>
                          <div className="text-sm text-gray-500">
                            {data.correct_bets || 0}/{data.total_bets || 0} correct predictions
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-6">
                        <div className="text-right">
                          <div className="font-medium text-gray-900">{data.win_rate?.toFixed(3) || 'N/A'}</div>
                          <div className="text-sm text-gray-500">Win Rate</div>
                        </div>
                        <div className="text-right">
                          <div className={`font-medium ${getPerformanceColor(data.roi || 0)}`}>
                            {data.roi?.toFixed(1) || 'N/A'}%
                          </div>
                          <div className="text-sm text-gray-500">ROI</div>
                        </div>
                        <span className={getPerformanceBadge(data.roi || 0)}>
                          {data.roi && data.roi > 5 ? 'Excellent' : data.roi && data.roi > 0 ? 'Profitable' : data.roi && data.roi > -5 ? 'Break-even' : 'Losing'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Predictions Tab */}
            {activeTab === 'predictions' && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Sample Predictions</h3>
                <div className="space-y-4">
                  {results.sample_predictions && results.sample_predictions.map((pred, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-4">
                        <div>
                          <div className="font-medium text-gray-900">{pred.game}</div>
                          <div className="text-sm text-gray-500">
                            {pred.date} • Spread: {pred.spread || 'N/A'}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-6">
                        <div className="text-right">
                          <div className="font-medium text-gray-900">{pred.predicted || 'N/A'}</div>
                          <div className="text-sm text-gray-500">Predicted</div>
                        </div>
                        <div className="text-right">
                          <div className="font-medium text-gray-900">{pred.actual || 'N/A'}</div>
                          <div className="text-sm text-gray-500">Actual</div>
                        </div>
                        <div className="text-right">
                          <div className="font-medium text-gray-900">{pred.confidence?.toFixed(3) || 'N/A'}</div>
                          <div className="text-sm text-gray-500">Confidence</div>
                        </div>
                        <div className="flex items-center">
                          {pred.correct === true ? (
                            <span className="text-green-500 text-xl">✓</span>
                          ) : pred.correct === false ? (
                            <span className="text-red-500 text-xl">✗</span>
                          ) : (
                            <span className="text-gray-500 text-xl">?</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* No Results State */}
        {!results && !loading && (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-6xl mb-4">📊</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Backtest Results</h3>
            <p className="text-gray-500 mb-6">
              Click "Run Backtest" to test your model on historical data
            </p>
          </div>
        )}
      </div>
    </div>
  );
}