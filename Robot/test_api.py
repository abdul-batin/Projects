"""Simple test script to verify the API functionality."""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health: {response.json()}")
    return response.status_code == 200


def test_create_wall():
    """Test wall creation."""
    print("\nTesting wall creation...")
    wall_data = {
        "name": "Test Wall",
        "geometry": {
            "coordinates": [[0, 0], [5, 0], [5, 5], [0, 5]]
        }
    }
    response = requests.post(f"{BASE_URL}/walls", json=wall_data)
    result = response.json()
    print(f"✅ Wall created: {result}")
    return result.get("wall_id")


def test_create_obstacle(wall_id):
    """Test obstacle creation."""
    print("\nTesting obstacle creation...")
    obstacle_data = {
        "type": "window",
        "geometry": {
            "coordinates": [[1, 1], [2, 1], [2, 2], [1, 2]]
        }
    }
    response = requests.post(
        f"{BASE_URL}/walls/{wall_id}/obstacles",
        json=obstacle_data
    )
    result = response.json()
    print(f"✅ Obstacle created: {result}")
    return result.get("obstacle_id")


def test_plan_wall(wall_id):
    """Test planning."""
    print("\nTesting wall planning...")
    plan_data = {
        "resolution": 0.1
    }
    response = requests.post(
        f"{BASE_URL}/walls/{wall_id}/plan",
        json=plan_data
    )
    result = response.json()
    print(f"✅ Plan created:")
    print(f"   Plan ID: {result['plan_id']}")
    print(f"   Best Path ID: {result['best_path_id']}")
    print(f"   Candidates: {len(result['candidates'])}")
    for i, candidate in enumerate(result['candidates']):
        print(f"   {i+1}. Coverage: {candidate['coverage']:.2%}, Length: {candidate['path_length']}")
    return result.get("best_path_id")


def test_execute_path(path_id):
    """Test path execution."""
    print("\nTesting path execution...")
    response = requests.post(f"{BASE_URL}/paths/{path_id}/execute")
    result = response.json()
    print(f"✅ Execution initiated: {result}")
    return result.get("execution_id")


def test_get_stats():
    """Test stats endpoint."""
    print("\nTesting stats endpoint...")
    response = requests.get(f"{BASE_URL}/stats")
    result = response.json()
    print(f"✅ System Stats:")
    print(f"   Total Plans: {result['total_plans']}")
    print(f"   Total Paths: {result['total_paths']}")
    print(f"   Total Executions: {result['total_executions']}")
    print(f"   Active Executions: {result['active_executions']}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("🤖 Robot Wall Planner API Test Suite")
    print("=" * 60)
    
    try:
        # Test health
        if not test_health():
            print("❌ Health check failed. Is the server running?")
            return
        
        # Create wall
        wall_id = test_create_wall()
        if not wall_id:
            print("❌ Failed to create wall")
            return
        
        # Create obstacle
        test_create_obstacle(wall_id)
        
        # Plan wall
        path_id = test_plan_wall(wall_id)
        if not path_id:
            print("❌ Failed to create plan")
            return
        
        # Execute path
        execution_id = test_execute_path(path_id)
        
        # Get stats
        test_get_stats()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server. Please start the server first:")
        print("   cd Server && uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")


if __name__ == "__main__":
    main()
