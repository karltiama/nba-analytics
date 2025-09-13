'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface TreeNode {
  id: string;
  feature: string;
  threshold: number;
  samples: number;
  value: [number, number]; // [class_0_count, class_1_count]
  children?: {
    left?: TreeNode;
    right?: TreeNode;
  };
  isLeaf: boolean;
  prediction: number;
  confidence: number;
}

interface DecisionTreeVisualizationProps {
  modelName?: string;
  gameData?: any;
}

const DecisionTreeVisualization: React.FC<DecisionTreeVisualizationProps> = ({ 
  modelName = 'Random Forest',
  gameData 
}) => {
  const [selectedPath, setSelectedPath] = useState<string[]>([]);
  const [showDetails, setShowDetails] = useState(false);

  // Sample decision tree structure (simplified for visualization)
  const sampleTree: TreeNode = {
    id: 'root',
    feature: 'spread',
    threshold: -3.5,
    samples: 1000,
    value: [400, 600],
    isLeaf: false,
    prediction: 1,
    confidence: 0.6,
    children: {
      left: {
        id: 'left_1',
        feature: 'home_win_rate',
        threshold: 0.65,
        samples: 400,
        value: [200, 200],
        isLeaf: false,
        prediction: 0,
        confidence: 0.5,
        children: {
          left: {
            id: 'left_1_left',
            feature: 'home_recent_form_5',
            threshold: 0.6,
            samples: 200,
            value: [120, 80],
            isLeaf: false,
            prediction: 0,
            confidence: 0.6,
            children: {
              left: {
                id: 'left_1_left_left',
                feature: '',
                threshold: 0,
                samples: 120,
                value: [80, 40],
                isLeaf: true,
                prediction: 0,
                confidence: 0.67
              },
              right: {
                id: 'left_1_left_right',
                feature: '',
                threshold: 0,
                samples: 80,
                value: [30, 50],
                isLeaf: true,
                prediction: 1,
                confidence: 0.625
              }
            }
          },
          right: {
            id: 'left_1_right',
            feature: '',
            threshold: 0,
            samples: 200,
            value: [60, 140],
            isLeaf: true,
            prediction: 1,
            confidence: 0.7
          }
        }
      },
      right: {
        id: 'right_1',
        feature: 'away_point_differential',
        threshold: 2.0,
        samples: 600,
        value: [200, 400],
        isLeaf: false,
        prediction: 1,
        confidence: 0.67,
        children: {
          left: {
            id: 'right_1_left',
            feature: 'total',
            threshold: 225,
            samples: 200,
            value: [100, 100],
            isLeaf: false,
            prediction: 0,
            confidence: 0.5,
            children: {
              left: {
                id: 'right_1_left_left',
                feature: '',
                threshold: 0,
                samples: 100,
                value: [70, 30],
                isLeaf: true,
                prediction: 0,
                confidence: 0.7
              },
              right: {
                id: 'right_1_left_right',
                feature: '',
                threshold: 0,
                samples: 100,
                value: [30, 70],
                isLeaf: true,
                prediction: 1,
                confidence: 0.7
              }
            }
          },
          right: {
            id: 'right_1_right',
            feature: '',
            threshold: 0,
            samples: 400,
            value: [80, 320],
            isLeaf: true,
            prediction: 1,
            confidence: 0.8
          }
        }
      }
    }
  };

  const renderNode = (node: TreeNode, level: number = 0, path: string[] = []): JSX.Element => {
    const isSelected = selectedPath.includes(node.id);
    const isPath = selectedPath.length > 0 && selectedPath.includes(node.id);
    
    return (
      <div key={node.id} className="relative">
        <div 
          className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
            isSelected 
              ? 'border-blue-500 bg-blue-50 shadow-lg' 
              : isPath
              ? 'border-green-300 bg-green-50'
              : 'border-gray-200 bg-white hover:bg-gray-50'
          }`}
          onClick={() => setSelectedPath(path)}
          style={{ marginLeft: level * 20 }}
        >
          <div className="flex items-center gap-2 mb-2">
            <Badge variant={node.isLeaf ? 'secondary' : 'default'}>
              {node.isLeaf ? 'Leaf' : 'Decision'}
            </Badge>
            <span className="text-sm font-medium">
              {node.samples} samples
            </span>
          </div>
          
          {!node.isLeaf && (
            <div className="text-sm">
              <div className="font-semibold text-blue-600">
                {node.feature} ≤ {node.threshold}
              </div>
              <div className="text-gray-600">
                {node.feature === 'spread' && 'Point spread from sportsbooks'}
                {node.feature === 'home_win_rate' && 'Home team win percentage'}
                {node.feature === 'away_point_differential' && 'Away team point differential'}
                {node.feature === 'home_recent_form_5' && 'Home team last 5 games'}
                {node.feature === 'total' && 'Over/under total points'}
              </div>
            </div>
          )}
          
          {node.isLeaf && (
            <div className="text-sm">
              <div className="font-semibold text-green-600">
                Prediction: {node.prediction === 1 ? 'Home Covers' : 'Away Covers'}
              </div>
              <div className="text-gray-600">
                Confidence: {(node.confidence * 100).toFixed(1)}%
              </div>
            </div>
          )}
          
          <div className="mt-2 text-xs text-gray-500">
            Distribution: {node.value[0]} vs {node.value[1]}
          </div>
        </div>
        
        {node.children && (
          <div className="mt-4 space-y-4">
            {node.children.left && (
              <div>
                <div className="text-xs text-gray-500 mb-1">Yes (≤ {node.threshold})</div>
                {renderNode(node.children.left, level + 1, [...path, node.children.left.id])}
              </div>
            )}
            {node.children.right && (
              <div>
                <div className="text-xs text-gray-500 mb-1">No (&gt; {node.threshold})</div>
                {renderNode(node.children.right, level + 1, [...path, node.children.right.id])}
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  const getSelectedNode = (): TreeNode | null => {
    if (selectedPath.length === 0) return null;
    
    let current = sampleTree;
    for (const id of selectedPath) {
      if (current.children?.left?.id === id) {
        current = current.children.left;
      } else if (current.children?.right?.id === id) {
        current = current.children.right;
      } else {
        return null;
      }
    }
    return current;
  };

  const selectedNode = getSelectedNode();

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🌳 Decision Tree Visualization
            <Badge variant="secondary">Educational</Badge>
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            See how {modelName} makes decisions by following the tree structure
          </p>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 items-center">
            <Button 
              variant="outline" 
              onClick={() => setShowDetails(!showDetails)}
            >
              {showDetails ? 'Hide' : 'Show'} Detailed Info
            </Button>
            <Button 
              variant="outline" 
              onClick={() => setSelectedPath([])}
            >
              Clear Selection
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Tree Visualization */}
      <Card>
        <CardHeader>
          <CardTitle>🌲 Decision Tree Structure</CardTitle>
          <p className="text-sm text-muted-foreground">
            Click on any node to see detailed information. Follow the path from root to leaf.
          </p>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <div className="min-w-max">
              {renderNode(sampleTree)}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Selected Node Details */}
      {selectedNode && (
        <Card>
          <CardHeader>
            <CardTitle>🔍 Selected Node Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-blue-600">Node Information</h4>
                  <div className="text-sm space-y-1">
                    <div><strong>Node ID:</strong> {selectedNode.id}</div>
                    <div><strong>Type:</strong> {selectedNode.isLeaf ? 'Leaf Node' : 'Decision Node'}</div>
                    <div><strong>Samples:</strong> {selectedNode.samples}</div>
                    <div><strong>Distribution:</strong> {selectedNode.value[0]} vs {selectedNode.value[1]}</div>
                  </div>
                </div>
                
                {!selectedNode.isLeaf && (
                  <div>
                    <h4 className="font-semibold text-green-600">Decision Rule</h4>
                    <div className="text-sm space-y-1">
                      <div><strong>Feature:</strong> {selectedNode.feature}</div>
                      <div><strong>Threshold:</strong> {selectedNode.threshold}</div>
                      <div><strong>Rule:</strong> If {selectedNode.feature} &le; {selectedNode.threshold}, go left</div>
                    </div>
                  </div>
                )}
                
                {selectedNode.isLeaf && (
                  <div>
                    <h4 className="font-semibold text-purple-600">Final Prediction</h4>
                    <div className="text-sm space-y-1">
                      <div><strong>Prediction:</strong> {selectedNode.prediction === 1 ? 'Home Team Covers' : 'Away Team Covers'}</div>
                      <div><strong>Confidence:</strong> {(selectedNode.confidence * 100).toFixed(1)}%</div>
                      <div><strong>Support:</strong> {selectedNode.value[selectedNode.prediction]} out of {selectedNode.samples} samples</div>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-orange-600">Path to This Node</h4>
                  <div className="text-sm">
                    {selectedPath.map((id, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <span className="text-gray-400">→</span>
                        <Badge variant="outline" className="text-xs">
                          {id}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
                
                {showDetails && (
                  <div>
                    <h4 className="font-semibold text-red-600">Technical Details</h4>
                    <div className="text-sm space-y-1">
                      <div><strong>Gini Impurity:</strong> {((selectedNode.value[0] / selectedNode.samples) * (selectedNode.value[1] / selectedNode.samples) * 2).toFixed(3)}</div>
                      <div><strong>Information Gain:</strong> {((selectedNode.value[0] / selectedNode.samples) * Math.log2(selectedNode.value[0] / selectedNode.samples) + (selectedNode.value[1] / selectedNode.samples) * Math.log2(selectedNode.value[1] / selectedNode.samples)).toFixed(3)}</div>
                      <div><strong>Class Purity:</strong> {Math.max(selectedNode.value[0], selectedNode.value[1]) / selectedNode.samples * 100}%</div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* How Random Forest Works */}
      <Card>
        <CardHeader>
          <CardTitle>🧠 How Random Forest Works</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-semibold text-green-600">✅ Tree Creation Process:</h4>
              <ol className="text-sm space-y-1 list-decimal list-inside">
                <li>Random Forest creates 200 different decision trees</li>
                <li>Each tree uses a random subset of training data (bootstrap sampling)</li>
                <li>Each tree considers only a random subset of features at each split</li>
                <li>This randomness reduces overfitting and improves generalization</li>
                <li>Each tree makes its own prediction independently</li>
              </ol>
            </div>
            <div className="space-y-3">
              <h4 className="font-semibold text-blue-600">🎯 Prediction Process:</h4>
              <ol className="text-sm space-y-1 list-decimal list-inside">
                <li>New game data is fed to all 200 trees</li>
                <li>Each tree follows its own decision path to make a prediction</li>
                <li>All 200 predictions are collected (votes)</li>
                <li>Final prediction is the majority vote across all trees</li>
                <li>Confidence is the percentage of trees that agree</li>
              </ol>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Learning Insights */}
      <Card>
        <CardHeader>
          <CardTitle>🎓 Key Learning Points</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-semibold text-purple-600">🌳 Decision Tree Concepts:</h4>
              <ul className="text-sm space-y-1 list-disc list-inside">
                <li><strong>Root Node:</strong> Starting point with all training data</li>
                <li><strong>Internal Nodes:</strong> Decision points that split data</li>
                <li><strong>Leaf Nodes:</strong> Final predictions with no more splits</li>
                <li><strong>Splitting Criteria:</strong> Features and thresholds that best separate classes</li>
                <li><strong>Pruning:</strong> Removing branches that don't improve performance</li>
              </ul>
            </div>
            <div className="space-y-3">
              <h4 className="font-semibold text-orange-600">🎲 Random Forest Benefits:</h4>
              <ul className="text-sm space-y-1 list-disc list-inside">
                <li><strong>Reduced Overfitting:</strong> Multiple trees prevent memorizing training data</li>
                <li><strong>Better Generalization:</strong> Works well on new, unseen data</li>
                <li><strong>Feature Importance:</strong> Can identify which features matter most</li>
                <li><strong>Robustness:</strong> Less sensitive to outliers and noise</li>
                <li><strong>Confidence Scores:</strong> Natural way to measure prediction certainty</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DecisionTreeVisualization;
