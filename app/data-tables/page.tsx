'use client';

import { useState } from 'react';
import DataQualityDashboard from '@/components/DataQualityDashboard';
import TeamsTable from '@/components/tables/TeamsTable';
import GamesTable from '@/components/tables/GamesTable';
import TeamStatsTable from '@/components/tables/TeamStatsTable';

type TabType = 'dashboard' | 'teams' | 'games' | 'stats';

const DataTablesPage = () => {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');

  const tabs = [
    { id: 'dashboard' as TabType, label: 'Data Quality', icon: '📊' },
    { id: 'teams' as TabType, label: 'Teams', icon: '🏀' },
    { id: 'games' as TabType, label: 'Games', icon: '🎯' },
    { id: 'stats' as TabType, label: 'Team Stats', icon: '📈' }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DataQualityDashboard />;
      case 'teams':
        return <TeamsTable />;
      case 'games':
        return <GamesTable />;
      case 'stats':
        return <TeamStatsTable />;
      default:
        return <DataQualityDashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <h1 className="text-3xl font-bold text-gray-900">NBA Data Tables</h1>
            <p className="mt-2 text-gray-600">
              Explore and verify your NBA data quality before building betting models
            </p>
          </div>
          
          {/* Tab Navigation */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderContent()}
      </div>
    </div>
  );
};

export default DataTablesPage;
