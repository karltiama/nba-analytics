
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            NBA Analytics Dashboard
          </h1>
          <p className="text-xl text-black mb-12 max-w-2xl mx-auto">
            Advanced NBA statistics, team performance analysis, and player insights 
            powered by machine learning for betting predictions.
          </p>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
            {/* Model Testing Card */}
            <div className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition-shadow">
              <div className="text-4xl mb-4">🤖</div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Model Testing</h2>
              <p className="text-black mb-6">
                Test and compare different ML models with comprehensive backtesting 
                and performance analytics.
              </p>
              <div className="space-y-2">
                <Link 
                  href="/backtest-dashboard"
                  className="inline-block bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
                >
                  Test Models
                </Link>
              </div>
            </div>

            {/* Data Tables Card */}
            <div className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition-shadow">
              <div className="text-4xl mb-4">📊</div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Data Tables</h2>
              <p className="text-black mb-6">
                Explore and verify your NBA data quality with interactive tables for 
                teams, games, and statistics.
              </p>
              <div className="space-y-2">
                <Link 
                  href="/data-tables"
                  className="inline-block bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors"
                >
                  View Data Tables
                </Link>
                <br />
                <Link 
                  href="/test-tables"
                  className="inline-block bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors text-sm"
                >
                  Test Tables (Simple)
                </Link>
              </div>
            </div>

            {/* Team Stats Card */}
            <div className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition-shadow">
              <div className="text-4xl mb-4">🏀</div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Team Statistics</h2>
              <p className="text-black mb-6">
                View comprehensive team performance metrics including wins, losses, 
                points per game, shooting percentages, and more.
              </p>
              <Link 
                href="/dashboard"
                className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
              >
                View Team Stats
              </Link>
            </div>

            {/* Player Stats Card */}
            <div className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition-shadow">
              <div className="text-4xl mb-4">👤</div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Player Statistics</h2>
              <p className="text-black mb-6">
                Explore individual player performance with detailed stats including 
                points, rebounds, assists, and shooting efficiency.
              </p>
              <Link 
                href="/dashboard"
                className="inline-block bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
              >
                View Player Stats
              </Link>
            </div>

            {/* Backtest Card */}
            <div className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition-shadow">
              <div className="text-4xl mb-4">🎯</div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Model Backtest</h2>
              <p className="text-black mb-6">
                Test your NBA betting model on historical data to validate performance 
                and analyze ROI across different seasons.
              </p>
              <div className="space-y-2">
                <Link 
                  href="/backtest"
                  className="inline-block bg-orange-600 text-white px-6 py-3 rounded-lg hover:bg-orange-700 transition-colors"
                >
                  Run Backtest
                </Link>
                <br />
                <Link 
                  href="/model-flow"
                  className="inline-block bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                  Model Flow Visualization
                </Link>
              </div>
            </div>
          </div>

          <div className="mt-16">
            <h3 className="text-2xl font-semibold text-gray-900 mb-8">Features</h3>
            <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
              <div className="text-center">
                <div className="text-3xl mb-3">📊</div>
                <h4 className="font-semibold text-gray-900 mb-2">Interactive Tables</h4>
                <p className="text-black text-sm">Sort, filter, and analyze data with AG Grid</p>
              </div>
              <div className="text-center">
                <div className="text-3xl mb-3">🤖</div>
                <h4 className="font-semibold text-gray-900 mb-2">ML Predictions</h4>
                <p className="text-black text-sm">AI-powered betting predictions and insights</p>
              </div>
              <div className="text-center">
                <div className="text-3xl mb-3">📈</div>
                <h4 className="font-semibold text-gray-900 mb-2">Data Visualization</h4>
                <p className="text-black text-sm">Charts and graphs for better insights</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
