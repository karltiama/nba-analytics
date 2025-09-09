'use client';

import { useState, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

interface Prediction {
  game: {
    id: string;
    gameDate: string;
    homeTeam: { abbreviation: string; name: string };
    awayTeam: { abbreviation: string; name: string };
    spread: number;
    total: number;
    whosFavored: string;
  };
  prediction: {
    id: string;
    predictedValue: number;
    confidence: number;
    createdAt: string;
  };
  recommendation: {
    shouldBet: boolean;
    betType: string | null;
    confidence: number;
    recommendation: string;
  };
}

export default function PredictionsPage() {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modelInfo, setModelInfo] = useState<any>(null);

  useEffect(() => {
    fetchPredictions();
  }, []);

  const fetchPredictions = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/predictions?limit=20');
      const data = await response.json();
      
      if (data.success) {
        setPredictions(data.data);
        setModelInfo(data.modelInfo);
      } else {
        setError(data.error || 'Failed to fetch predictions');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  const columnDefs = [
    {
      headerName: 'Date',
      field: 'game.gameDate',
      valueFormatter: (params: any) => new Date(params.value).toLocaleDateString(),
      width: 100,
      pinned: 'left'
    },
    {
      headerName: 'Matchup',
      field: 'game',
      valueFormatter: (params: any) => {
        const game = params.value;
        return `${game.awayTeam.abbreviation} @ ${game.homeTeam.abbreviation}`;
      },
      width: 150,
      pinned: 'left'
    },
    {
      headerName: 'Spread',
      field: 'game.spread',
      valueFormatter: (params: any) => {
        const spread = params.value;
        const favored = params.data.game.whosFavored;
        return favored === 'home' ? `-${spread}` : `+${spread}`;
      },
      width: 80
    },
    {
      headerName: 'Total',
      field: 'game.total',
      width: 80
    },
    {
      headerName: 'Prediction',
      field: 'prediction.predictedValue',
      valueFormatter: (params: any) => {
        return params.value === 1 ? 'Favorite Covers' : 'Underdog Covers';
      },
      width: 140,
      cellStyle: (params: any) => {
        return params.value === 1 
          ? { backgroundColor: '#e8f5e8', color: '#2e7d32' }
          : { backgroundColor: '#fff3e0', color: '#f57c00' };
      }
    },
    {
      headerName: 'Confidence',
      field: 'prediction.confidence',
      valueFormatter: (params: any) => `${(params.value * 100).toFixed(1)}%`,
      width: 100,
      cellStyle: (params: any) => {
        const confidence = params.value;
        if (confidence >= 0.7) return { backgroundColor: '#e8f5e8' };
        if (confidence >= 0.6) return { backgroundColor: '#fff3e0' };
        return { backgroundColor: '#ffebee' };
      }
    },
    {
      headerName: 'Recommendation',
      field: 'recommendation',
      valueFormatter: (params: any) => {
        const rec = params.value;
        return rec.shouldBet ? '✅ BET' : '❌ NO BET';
      },
      width: 120,
      cellStyle: (params: any) => {
        const rec = params.value;
        return rec.shouldBet 
          ? { backgroundColor: '#e8f5e8', fontWeight: 'bold' }
          : { backgroundColor: '#ffebee', fontWeight: 'bold' };
      }
    },
    {
      headerName: 'Bet Type',
      field: 'recommendation.betType',
      width: 140
    },
    {
      headerName: 'Details',
      field: 'recommendation.recommendation',
      width: 300,
      wrapText: true,
      autoHeight: true
    }
  ];

  const defaultColDef = {
    sortable: true,
    filter: true,
    resizable: true
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex justify-center items-center h-64">
          <div className="text-lg">Loading predictions...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          Error: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">NBA Betting Predictions</h1>
        <p className="text-gray-600">
          AI-powered predictions for NBA point spreads using advanced machine learning
        </p>
        
        {modelInfo && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-800">Model Information</h3>
            <p className="text-blue-700">
              <strong>Model:</strong> {modelInfo.name} v{modelInfo.version} | 
              <strong> Confidence Threshold:</strong> {(modelInfo.threshold * 100).toFixed(1)}%
            </p>
          </div>
        )}
      </div>

      <div className="mb-4 flex justify-between items-center">
        <h2 className="text-xl font-semibold">Upcoming Games</h2>
        <button
          onClick={fetchPredictions}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Refresh Predictions
        </button>
      </div>

      <div className="ag-theme-alpine" style={{ height: '600px', width: '100%' }}>
        <AgGridReact
          rowData={predictions}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          pagination={true}
          paginationPageSize={20}
          suppressRowHoverHighlight={true}
        />
      </div>

      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-semibold mb-2">How to Use These Predictions</h3>
        <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
          <li><strong>✅ BET:</strong> Model recommends betting on this game (confidence above threshold)</li>
          <li><strong>❌ NO BET:</strong> Model recommends avoiding this game (confidence too low)</li>
          <li><strong>Confidence:</strong> Higher confidence means more reliable prediction</li>
          <li><strong>Bet Type:</strong> Whether to bet on favorite covering or underdog covering</li>
          <li><strong>Risk Management:</strong> Only bet what you can afford to lose</li>
        </ul>
      </div>
    </div>
  );
}
