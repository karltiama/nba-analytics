'use client';

import { useState } from 'react';

interface ModelResult {
  model_type: string;
  accuracy: number;
  win_rate: number;
  roi: number;
  total_bets: number;
  correct_bets: number;
  avg_confidence: number;
}

export default function ModelComparePage() {
  const [results, setResults] = useState<ModelResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.6);

  const runComparison = async () => {
    setLoading(true);
    setError(null);
    setResults([]);
    
    const models = ['basic', 'advanced', 'xgboost'];
    const comparisonResults: ModelResult[] = [];
    
    try {
      for (const model of models) {
        console.log(`Testing ${model} model...`);
        
        const response = await fetch('/api/backtest', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            season_start: '2020-21',
            season_end: '2024-25',
            confidence_threshold: confidenceThreshold,
            model_type: model
          })
        });

        if (response.ok) {
          const data = await response.json();
          if (data.accuracy !== undefined) {
            comparisonResults.push({
              model_type: model,
              accuracy: data.accuracy,
              win_rate: data.win_rate,
              roi: data.roi,
              total_bets: data.total_bets,
              correct_bets: data.correct_bets,
              avg_confidence: data.avg_confidence
            });
          }
        }
        
        // Small delay between requests
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      setResults(comparisonResults);
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

  const getBestModel = () => {
    if (results.length === 0) return null;
    return results.reduce((best, current) => 
      current.roi > best.roi ? current : best
    );
  };

  const bestModel = getBestModel();

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Model Comparison</h1>
            <p className="text-gray-600 mt-2">
              Compare different ML models side by side
            </p>
          </div>
          <div className="flex items-center gap-4">
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
              onClick={runComparison} 
              disabled={loading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Comparing Models...
                </>
              ) : (
                <>
                  <span>⚖️</span>
                  Compare Models
                </>
              )}
            </button>
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

        {/* Best Model Highlight */}
        {bestModel && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2 text-green-800">
              <span>🏆</span>
              <div>
                <div className="font-medium">Best Performing Model: {bestModel.model_type.toUpperCase()}</div>
                <div className="text-sm">
                  ROI: {bestModel.roi.toFixed(1)}% | Win Rate: {bestModel.win_rate.toFixed(3)} | 
                  Total Bets: {bestModel.total_bets}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results Table */}
        {results.length > 0 && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Model Performance Comparison</h3>
              <p className="text-sm text-gray-600 mt-1">
                Confidence Threshold: {confidenceThreshold} | Test Period: 2020-21 to 2023-24
              </p>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Model
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Accuracy
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Win Rate
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ROI
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total Bets
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Correct Bets
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Avg Confidence
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Performance
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {results.map((result, index) => (
                    <tr key={result.model_type} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="text-sm font-medium text-gray-900 capitalize">
                            {result.model_type}
                          </div>
                          {bestModel && result.model_type === bestModel.model_type && (
                            <span className="ml-2 text-yellow-500">👑</span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {result.accuracy.toFixed(3)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {result.win_rate.toFixed(3)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`text-sm font-medium ${getPerformanceColor(result.roi)}`}>
                          {result.roi.toFixed(1)}%
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {result.total_bets}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {result.correct_bets}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {result.avg_confidence.toFixed(3)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={getPerformanceBadge(result.roi)}>
                          {result.roi > 5 ? 'Excellent' : result.roi > 0 ? 'Profitable' : result.roi > -5 ? 'Break-even' : 'Losing'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* No Results State */}
        {results.length === 0 && !loading && (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-6xl mb-4">⚖️</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Comparison Results</h3>
            <p className="text-gray-500 mb-6">
              Click "Compare Models" to test all available models
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
