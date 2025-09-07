'use client';

import { useState } from 'react';

const TestTablesPage = () => {
  const [testData, setTestData] = useState([
    { id: 1, name: 'Lakers', city: 'Los Angeles', conference: 'Western' },
    { id: 2, name: 'Celtics', city: 'Boston', conference: 'Eastern' },
    { id: 3, name: 'Warriors', city: 'San Francisco', conference: 'Western' }
  ]);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Test Tables Page</h1>
      
      <div className="mb-4">
        <h2 className="text-xl font-semibold mb-2">Simple Test Table</h2>
        <table className="min-w-full bg-white border border-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Team</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">City</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Conference</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {testData.map((team) => (
              <tr key={team.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {team.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {team.city}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {team.conference}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-2">API Test</h2>
        <button 
          onClick={async () => {
            try {
              const response = await fetch('/api/teams');
              const data = await response.json();
              console.log('API Response:', data);
              alert('Check console for API response');
            } catch (error) {
              console.error('API Error:', error);
              alert('API Error - check console');
            }
          }}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Test Teams API
        </button>
      </div>
    </div>
  );
};

export default TestTablesPage;
