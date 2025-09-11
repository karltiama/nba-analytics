'use client';

import { useState, useEffect } from 'react';

interface FlowStep {
  id: string;
  title: string;
  icon: string;
  description: string;
  input?: string;
  output?: string;
  details: string[];
  isActive: boolean;
}

export default function ModelFlowVisualization() {
  const [currentStep, setCurrentStep] = useState(0);
  const [isRunning, setIsRunning] = useState(false);

  const flowSteps: FlowStep[] = [
    {
      id: 'raw-data',
      title: 'Raw Game Data',
      icon: '📊',
      description: 'Input from your database',
      input: 'Games, Teams, Stats',
      output: 'Structured data',
      details: [
        'Game: DAL @ BOS',
        'Spread: 6.5 points',
        'BOS win rate: 0.900',
        'DAL win rate: 0.500',
        'Recent form, rest days...'
      ],
      isActive: false
    },
    {
      id: 'features',
      title: 'Feature Engineering',
      icon: '🔧',
      description: 'Transform into 29 features',
      input: 'Raw data',
      output: '29 numerical features',
      details: [
        'win_rate_difference: 0.400',
        'point_differential_difference: 3.700',
        'recent_form_difference: 0.400',
        'rest_days_difference: 0.000',
        'season_progress: 0.956...'
      ],
      isActive: false
    },
    {
      id: 'model',
      title: 'ML Model',
      icon: '🤖',
      description: 'Gradient Boosting Classifier',
      input: '29 features',
      output: 'Prediction + Confidence',
      details: [
        '100 decision trees',
        '6 levels deep each',
        'Learning rate: 0.1',
        'Sequential boosting',
        'Votes combined → Final prediction'
      ],
      isActive: false
    },
    {
      id: 'prediction',
      title: 'Prediction',
      icon: '🎯',
      description: 'Model output',
      input: '29 features',
      output: '[0.3, 0.7] → 1 (BOS covers)',
      details: [
        'Probabilities: [0.3, 0.7]',
        'Prediction: 1 (favorite covers)',
        'Confidence: 0.7 (70% sure)',
        'Decision: Make bet?',
        'Threshold: 0.6'
      ],
      isActive: false
    },
    {
      id: 'betting',
      title: 'Betting Decision',
      icon: '🎲',
      description: 'Risk management',
      input: 'Prediction + Confidence',
      output: 'Bet or Skip',
      details: [
        'Confidence: 0.7 > 0.6 ✓',
        'Decision: BET on BOS',
        'Amount: $110 to win $100',
        'Outcome: BOS wins by 7+ points',
        'Result: Win $100'
      ],
      isActive: false
    },
    {
      id: 'performance',
      title: 'Performance',
      icon: '📈',
      description: 'Track results',
      input: 'Bet outcomes',
      output: 'ROI metrics',
      details: [
        'Total Bets: 260',
        'Correct: 145',
        'Win Rate: 55.8%',
        'ROI: 62.2%',
        'Sharpe Ratio: 0.825'
      ],
      isActive: false
    }
  ];

  const runSimulation = () => {
    setIsRunning(true);
    setCurrentStep(0);
    
    flowSteps.forEach((_, index) => {
      setTimeout(() => {
        setCurrentStep(index);
      }, index * 1000);
    });

    setTimeout(() => {
      setIsRunning(false);
    }, flowSteps.length * 1000);
  };

  const resetSimulation = () => {
    setIsRunning(false);
    setCurrentStep(0);
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-black mb-4">
          🏀 NBA Betting Model Flow
        </h2>
        <p className="text-lg text-black mb-6">
          Interactive visualization of your machine learning pipeline
        </p>
        
        <div className="space-x-4">
          <button
            onClick={runSimulation}
            disabled={isRunning}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isRunning ? 'Running...' : '▶️ Run Simulation'}
          </button>
          <button
            onClick={resetSimulation}
            className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            🔄 Reset
          </button>
        </div>
      </div>

      {/* Flow Steps */}
      <div className="space-y-6">
        {flowSteps.map((step, index) => (
          <div
            key={step.id}
            className={`transition-all duration-500 ${
              index <= currentStep
                ? 'opacity-100 transform translate-x-0'
                : 'opacity-50 transform translate-x-4'
            }`}
          >
            <div
              className={`bg-white rounded-lg shadow-lg p-6 border-l-4 ${
                index === currentStep
                  ? 'border-blue-500 bg-blue-50'
                  : index < currentStep
                  ? 'border-green-500 bg-green-50'
                  : 'border-gray-300'
              }`}
            >
              <div className="flex items-start space-x-4">
                <div className="text-4xl">{step.icon}</div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-xl font-bold text-black">
                      {step.title}
                    </h3>
                    <div className="flex items-center space-x-2">
                      {index < currentStep && (
                        <span className="text-green-600 text-sm">✅ Complete</span>
                      )}
                      {index === currentStep && (
                        <span className="text-blue-600 text-sm animate-pulse">
                          🔄 Processing...
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <p className="text-black mb-4">{step.description}</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    {step.input && (
                      <div className="bg-gray-100 rounded-lg p-3">
                        <div className="text-sm font-semibold text-black mb-1">
                          Input:
                        </div>
                        <div className="text-sm text-black">{step.input}</div>
                      </div>
                    )}
                    {step.output && (
                      <div className="bg-blue-100 rounded-lg p-3">
                        <div className="text-sm font-semibold text-black mb-1">
                          Output:
                        </div>
                        <div className="text-sm text-black font-mono">
                          {step.output}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="space-y-1">
                    {step.details.map((detail, detailIndex) => (
                      <div
                        key={detailIndex}
                        className={`text-sm transition-all duration-300 ${
                          index <= currentStep
                            ? 'text-black'
                            : 'text-black'
                        }`}
                        style={{
                          animationDelay: `${detailIndex * 100}ms`,
                          animation: index === currentStep ? 'fadeInUp 0.5s ease-out' : 'none'
                        }}
                      >
                        • {detail}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Data Flow Arrow */}
      <div className="flex justify-center mt-8">
        <div className="text-4xl text-gray-400 animate-bounce">↓</div>
      </div>

      {/* Performance Summary */}
      <div className="mt-8 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6">
        <h3 className="text-xl font-bold text-black mb-4 text-center">
          📊 Model Performance Summary
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">260</div>
            <div className="text-sm text-black">Total Bets</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">55.8%</div>
            <div className="text-sm text-black">Win Rate</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">62.2%</div>
            <div className="text-sm text-black">ROI</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">0.825</div>
            <div className="text-sm text-black">Avg Confidence</div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}
