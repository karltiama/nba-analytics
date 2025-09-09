#!/usr/bin/env python3
"""
Test script to verify ML service integration
"""
import requests
import json
import time

def test_ml_service():
    """Test the Python ML service"""
    print("🧪 Testing ML service...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ ML service is healthy")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ ML service health check failed: {response.status_code}")
            return False
            
        # Test prediction endpoint (using a sample game ID)
        # You'll need to replace this with an actual game ID from your database
        sample_game_id = "cmfbemkgd0a40kpd4xc7hvsq7"  # Replace with real game ID
        
        response = requests.post(f"http://localhost:8000/predict-game/{sample_game_id}")
        if response.status_code == 200:
            print("✅ ML service prediction working")
            prediction = response.json()
            print(f"   Prediction: {prediction['predicted_class']}")
            print(f"   Confidence: {prediction['confidence']:.3f}")
            print(f"   Recommendation: {prediction['recommendation']['recommendation']}")
        else:
            print(f"❌ ML service prediction failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to ML service. Make sure it's running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Error testing ML service: {e}")
        return False

def test_nextjs_api():
    """Test the Next.js API"""
    print("\n🧪 Testing Next.js API...")
    
    try:
        # Test predictions endpoint
        response = requests.get("http://localhost:3000/api/predictions?limit=5")
        if response.status_code == 200:
            print("✅ Next.js API is working")
            data = response.json()
            print(f"   Found {len(data['data'])} predictions")
            if data['data']:
                first_prediction = data['data'][0]
                print(f"   Sample prediction: {first_prediction['game']['awayTeam']['abbreviation']} @ {first_prediction['game']['homeTeam']['abbreviation']}")
                print(f"   Recommendation: {first_prediction['recommendation']['recommendation']}")
        else:
            print(f"❌ Next.js API failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Next.js API. Make sure it's running on port 3000")
        return False
    except Exception as e:
        print(f"❌ Error testing Next.js API: {e}")
        return False

def main():
    print("🎯 NBA Betting Analytics - Integration Test")
    print("=" * 50)
    
    # Test ML service
    ml_working = test_ml_service()
    
    if ml_working:
        # Test Next.js API
        api_working = test_nextjs_api()
        
        if api_working:
            print("\n🎉 All tests passed! Your NBA betting app is ready to use!")
            print("\n📱 Access your app at: http://localhost:3000")
            print("🔧 ML service running at: http://localhost:8000")
        else:
            print("\n❌ Next.js API tests failed. Check the Next.js app.")
    else:
        print("\n❌ ML service tests failed. Check the Python service.")

if __name__ == "__main__":
    main()
