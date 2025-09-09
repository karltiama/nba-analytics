'use client';

import { useState, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

interface UserBet {
  id: string;
  gameId: string;
  betType: string;
  betAmount: number;
  odds: number;
  potentialWin: number;
  actualWin: number | null;
  status: string;
  createdAt: string;
  game: {
    gameDate: string;
    homeTeam: { abbreviation: string; name: string };
    awayTeam: { abbreviation: string; name: string };
    spread: number;
    total: number;
  };
}

export default function BettingPage() {
  const [bets, setBets] = useState<UserBet[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showBetForm, setShowBetForm] = useState(false);
  const [selectedGame, setSelectedGame] = useState<any>(null);
  const [betForm, setBetForm] = useState({
    betType: 'spread',
    betAmount: 100,
    betSide: 'favorite'
  });

  useEffect(() => {
    fetchBets();
  }, []);

  const fetchBets = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/bets');
      const data = await response.json();
      
      if (data.success) {
        setBets(data.data);
      } else {
        setError(data.error || 'Failed to fetch bets');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  const placeBet = async () => {
    if (!selectedGame) return;

    try {
      const response = await fetch('/api/bets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          gameId: selectedGame.id,
          betType: betForm.betType,
          betAmount: betForm.betAmount,
          betSide: betForm.betSide,
          odds: -110 // Standard -110 odds
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        setShowBetForm(false);
        setSelectedGame(null);
        fetchBets(); // Refresh the list
      } else {
        setError(data.error || 'Failed to place bet');
      }
    } catch (err) {
      setError('Network error');
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
      headerName: 'Game',
      field: 'game',
      valueFormatter: (params: any) => {
        const game = params.value;
        return `${game.awayTeam.abbreviation} @ ${game.homeTeam.abbreviation}`;
      },
      width: 150,
      pinned: 'left'
    },
    {
      headerName: 'Bet Type',
      field: 'betType',
      width: 100
    },
    {
      headerName: 'Amount',
      field: 'betAmount',
      valueFormatter: (params: any) => `$${params.value}`,
      width: 100
    },
    {
      headerName: 'Odds',
      field: 'odds',
      valueFormatter: (params: any) => `${params.value > 0 ? '+' : ''}${params.value}`,
      width: 80
    },
    {
      headerName: 'Potential Win',
      field: 'potentialWin',
      valueFormatter: (params: any) => `$${params.value}`,
      width: 120
    },
    {
      headerName: 'Status',
      field: 'status',
      width: 100,
      cellStyle: (params: any) => {
        switch (params.value) {
          case 'pending': return { backgroundColor: '#fff3e0', color: '#f57c00' };
          case 'won': return { backgroundColor: '#e8f5e8', color: '#2e7d32' };
          case 'lost': return { backgroundColor: '#ffebee', color: '#d32f2f' };
          case 'pushed': return { backgroundColor: '#f3e5f5', color: '#7b1fa2' };
          default: return {};
        }
      }
    },
    {
      headerName: 'Actual Win',
      field: 'actualWin',
      valueFormatter: (params: any) => params.value ? `$${params.value}` : '-',
      width: 120
    },
    {
      headerName: 'Created',
      field: 'createdAt',
      valueFormatter: (params: any) => new Date(params.value).toLocaleString(),
      width: 150
    }
  ];

  const defaultColDef = {
    sortable: true,
    filter: true,
    resizable: true
  };

  // Calculate betting statistics
  const totalBets = bets.length;
  const wonBets = bets.filter(bet => bet.status === 'won').length;
  const lostBets = bets.filter(bet => bet.status === 'lost').length;
  const pushedBets = bets.filter(bet => bet.status === 'pushed').length;
  const pendingBets = bets.filter(bet => bet.status === 'pending').length;
  
  const totalWagered = bets.reduce((sum, bet) => sum + bet.betAmount, 0);
  const totalWon = bets
    .filter(bet => bet.actualWin !== null)
    .reduce((sum, bet) => sum + (bet.actualWin || 0), 0);
  const netProfit = totalWon - totalWagered;
  const roi = totalWagered > 0 ? (netProfit / totalWagered) * 100 : 0;

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex justify-center items-center h-64">
          <div className="text-lg">Loading betting history...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">My Betting History</h1>
        <p className="text-gray-600">
          Track your betting performance and ROI
        </p>
      </div>

      {/* Betting Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="font-semibold text-blue-800">Total Bets</h3>
          <p className="text-2xl font-bold text-blue-900">{totalBets}</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <h3 className="font-semibold text-green-800">Win Rate</h3>
          <p className="text-2xl font-bold text-green-900">
            {totalBets > 0 ? ((wonBets / (wonBets + lostBets)) * 100).toFixed(1) : 0}%
          </p>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <h3 className="font-semibold text-purple-800">Net Profit</h3>
          <p className={`text-2xl font-bold ${netProfit >= 0 ? 'text-green-900' : 'text-red-900'}`}>
            ${netProfit.toFixed(2)}
          </p>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg">
          <h3 className="font-semibold text-orange-800">ROI</h3>
          <p className={`text-2xl font-bold ${roi >= 0 ? 'text-green-900' : 'text-red-900'}`}>
            {roi.toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Detailed Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="text-center">
          <div className="text-lg font-semibold text-green-600">{wonBets}</div>
          <div className="text-sm text-gray-600">Won</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-semibold text-red-600">{lostBets}</div>
          <div className="text-sm text-gray-600">Lost</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-semibold text-purple-600">{pushedBets}</div>
          <div className="text-sm text-gray-600">Pushed</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-semibold text-orange-600">{pendingBets}</div>
          <div className="text-sm text-gray-600">Pending</div>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          Error: {error}
        </div>
      )}

      <div className="mb-4 flex justify-between items-center">
        <h2 className="text-xl font-semibold">Betting History</h2>
        <button
          onClick={() => setShowBetForm(true)}
          className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
        >
          Place New Bet
        </button>
      </div>

      <div className="ag-theme-alpine" style={{ height: '400px', width: '100%' }}>
        <AgGridReact
          rowData={bets}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          pagination={true}
          paginationPageSize={20}
        />
      </div>

      {/* Bet Form Modal */}
      {showBetForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-96">
            <h3 className="text-xl font-bold mb-4">Place New Bet</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Bet Type</label>
                <select
                  value={betForm.betType}
                  onChange={(e) => setBetForm({...betForm, betType: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="spread">Point Spread</option>
                  <option value="total">Total Points</option>
                  <option value="moneyline">Moneyline</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Bet Amount ($)</label>
                <input
                  type="number"
                  value={betForm.betAmount}
                  onChange={(e) => setBetForm({...betForm, betAmount: parseInt(e.target.value)})}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  min="1"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Bet Side</label>
                <select
                  value={betForm.betSide}
                  onChange={(e) => setBetForm({...betForm, betSide: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="favorite">Favorite</option>
                  <option value="underdog">Underdog</option>
                </select>
              </div>
            </div>
            
            <div className="mt-6 flex justify-end space-x-3">
              <button
                onClick={() => setShowBetForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={placeBet}
                className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
              >
                Place Bet
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
