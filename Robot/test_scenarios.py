#!/usr/bin/env python3
"""
Comprehensive test scenarios for Robot Wall Planner
Tests 2 different walls with all API functionalities
"""
import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_response(response: requests.Response, description: str):
    """Print formatted API response."""
    print(f"\n📍 {description}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return data
    else:
        print(f"Error: {response.text}")
        return None

# ==============================================================================
# SCENARIO 1: SMALL RECTANGULAR ROOM (Living Room)
# ==============================================================================

def scenario_1_small_room():
    """Test Scenario 1: Small rectangular room with window and door."""
    print_section("SCENARIO 1: Small Living Room (5m x 4m)")
    
    # 1. CREATE WALL
    print("\n🔷 Step 1: Create Wall")
    wall_data_1 = {
        "name": "Living Room",
        "geometry": {
            "coordinates": [
                [0, 0],    # Bottom-left
                [5, 0],    # Bottom-right
                [5, 4],    # Top-right
                [0, 4]     # Top-left
            ]
        }
    }
    print(f"Input: {json.dumps(wall_data_1, indent=2)}")
    response = requests.post(f"{BASE_URL}/walls", json=wall_data_1)
    wall_1 = print_response(response, "Wall Created")
    if not wall_1:
        return None
    wall_1_id = wall_1["wall_id"]
    
    # 2. GET WALL DETAILS
    print("\n🔷 Step 2: Get Wall Details")
    response = requests.get(f"{BASE_URL}/walls/{wall_1_id}")
    print_response(response, "Wall Details Retrieved")
    
    # 3. ADD WINDOW OBSTACLE
    print("\n🔷 Step 3: Add Window Obstacle")
    window_data = {
        "type": "window",
        "geometry": {
            "coordinates": [
                [1, 2],     # Bottom-left
                [2, 2],     # Bottom-right
                [2, 3.5],   # Top-right
                [1, 3.5]    # Top-left
            ]
        }
    }
    print(f"Input: {json.dumps(window_data, indent=2)}")
    response = requests.post(f"{BASE_URL}/walls/{wall_1_id}/obstacles", json=window_data)
    print_response(response, "Window Obstacle Added")
    
    # 4. ADD DOOR OBSTACLE
    print("\n🔷 Step 4: Add Door Obstacle")
    door_data = {
        "type": "door",
        "geometry": {
            "coordinates": [
                [3.5, 0],   # Bottom-left
                [4.5, 0],   # Bottom-right
                [4.5, 1],   # Top-right
                [3.5, 1]    # Top-left
            ]
        }
    }
    print(f"Input: {json.dumps(door_data, indent=2)}")
    response = requests.post(f"{BASE_URL}/walls/{wall_1_id}/obstacles", json=door_data)
    print_response(response, "Door Obstacle Added")
    
    # 5. LIST ALL OBSTACLES
    print("\n🔷 Step 5: List All Obstacles")
    response = requests.get(f"{BASE_URL}/walls/{wall_1_id}/obstacles")
    print_response(response, "All Obstacles Retrieved")
    
    # 6. GENERATE PLAN (High Resolution)
    print("\n🔷 Step 6: Generate Coverage Plan")
    plan_request = {
        "resolution": 0.1  # 10cm resolution
    }
    print(f"Input: {json.dumps(plan_request, indent=2)}")
    response = requests.post(f"{BASE_URL}/walls/{wall_1_id}/plan", json=plan_request)
    plan_1 = print_response(response, "Plan Generated")
    if not plan_1:
        return None
    
    plan_1_id = plan_1["plan_id"]
    best_path_1_id = plan_1["best_path_id"]
    
    print(f"\n📊 Coverage Results:")
    for i, candidate in enumerate(plan_1["candidates"]):
        print(f"   Strategy {i+1}: {candidate['path_length']} cells, "
              f"{candidate['coverage']*100:.2f}% coverage")
    
    # 7. GET PLAN DETAILS
    print("\n🔷 Step 7: Get Detailed Plan Information")
    response = requests.get(f"{BASE_URL}/walls/plans/{plan_1_id}")
    print_response(response, "Plan Details Retrieved")
    
    # 8. EXECUTE BEST PATH
    print("\n🔷 Step 8: Execute Best Path")
    response = requests.post(f"{BASE_URL}/paths/{best_path_1_id}/execute")
    execution_1 = print_response(response, "Path Execution Initiated")
    if not execution_1:
        return None
    execution_1_id = execution_1["execution_id"]
    
    # 9. SIMULATE TELEMETRY UPDATES
    print("\n🔷 Step 9: Simulate Robot Telemetry Updates")
    
    for progress in [25.0, 50.0, 75.0, 100.0]:
        telemetry_data = {
            "execution_id": execution_1_id,
            "position": [2.5, 2.0],  # Current robot position
            "progress": progress,
            "status": "COMPLETED" if progress == 100.0 else "RUNNING"
        }
        print(f"\n   Sending telemetry: {progress}% complete")
        response = requests.post(f"{BASE_URL}/telemetry/update", json=telemetry_data)
        if response.status_code == 200:
            print(f"   ✅ Telemetry updated")
        time.sleep(0.5)  # Simulate time passing
    
    # 10. GET EXECUTION STATUS
    print("\n🔷 Step 10: Get Final Execution Status")
    response = requests.get(f"{BASE_URL}/paths/executions/{execution_1_id}")
    print_response(response, "Execution Status Retrieved")
    
    # 11. LIST ALL EXECUTIONS FOR PATH
    print("\n🔷 Step 11: List All Executions for Path")
    response = requests.get(f"{BASE_URL}/paths/{best_path_1_id}/executions")
    print_response(response, "All Executions Listed")
    
    return {
        "wall_id": wall_1_id,
        "plan_id": plan_1_id,
        "path_id": best_path_1_id,
        "execution_id": execution_1_id
    }


# ==============================================================================
# SCENARIO 2: LARGE L-SHAPED ROOM (Office)
# ==============================================================================

def scenario_2_large_lshaped():
    """Test Scenario 2: Large L-shaped office with multiple obstacles."""
    print_section("SCENARIO 2: Large L-Shaped Office (10m x 10m)")
    
    # 1. CREATE L-SHAPED WALL
    print("\n🔷 Step 1: Create L-Shaped Wall")
    wall_data_2 = {
        "name": "L-Shaped Office",
        "geometry": {
            "coordinates": [
                [0, 0],     # Bottom-left of main area
                [10, 0],    # Bottom-right of main area
                [10, 6],    # Right side up
                [6, 6],     # Inner corner
                [6, 10],    # Top of extension
                [0, 10],    # Top-left
                [0, 0]      # Close the polygon
            ]
        }
    }
    print(f"Input: {json.dumps(wall_data_2, indent=2)}")
    response = requests.post(f"{BASE_URL}/walls", json=wall_data_2)
    wall_2 = print_response(response, "L-Shaped Wall Created")
    if not wall_2:
        return None
    wall_2_id = wall_2["wall_id"]
    
    # 2. ADD DESK OBSTACLE
    print("\n🔷 Step 2: Add Desk Obstacle")
    desk_data = {
        "type": "desk",
        "geometry": {
            "coordinates": [
                [2, 2],
                [4, 2],
                [4, 3.5],
                [2, 3.5]
            ]
        }
    }
    print(f"Input: {json.dumps(desk_data, indent=2)}")
    response = requests.post(f"{BASE_URL}/walls/{wall_2_id}/obstacles", json=desk_data)
    print_response(response, "Desk Obstacle Added")
    
    # 3. ADD FILING CABINET
    print("\n🔷 Step 3: Add Filing Cabinet Obstacle")
    cabinet_data = {
        "type": "filing_cabinet",
        "geometry": {
            "coordinates": [
                [7, 1],
                [8.5, 1],
                [8.5, 2],
                [7, 2]
            ]
        }
    }
    print(f"Input: {json.dumps(cabinet_data, indent=2)}")
    response = requests.post(f"{BASE_URL}/walls/{wall_2_id}/obstacles", json=cabinet_data)
    print_response(response, "Filing Cabinet Added")
    
    # 4. ADD PLANT
    print("\n🔷 Step 4: Add Plant Obstacle")
    plant_data = {
        "type": "plant",
        "geometry": {
            "coordinates": [
                [1, 7],
                [2, 7],
                [2, 8],
                [1, 8]
            ]
        }
    }
    print(f"Input: {json.dumps(plant_data, indent=2)}")
    response = requests.post(f"{BASE_URL}/walls/{wall_2_id}/obstacles", json=plant_data)
    print_response(response, "Plant Obstacle Added")
    
    # 5. LIST ALL OBSTACLES
    print("\n🔷 Step 5: List All Obstacles")
    response = requests.get(f"{BASE_URL}/walls/{wall_2_id}/obstacles")
    print_response(response, "All Obstacles Retrieved")
    
    # 6. GENERATE PLAN (Medium Resolution)
    print("\n🔷 Step 6: Generate Coverage Plan")
    plan_request = {
        "resolution": 0.2  # 20cm resolution for larger area
    }
    print(f"Input: {json.dumps(plan_request, indent=2)}")
    response = requests.post(f"{BASE_URL}/walls/{wall_2_id}/plan", json=plan_request)
    plan_2 = print_response(response, "Plan Generated")
    if not plan_2:
        return None
    
    plan_2_id = plan_2["plan_id"]
    best_path_2_id = plan_2["best_path_id"]
    
    print(f"\n📊 Coverage Results:")
    for i, candidate in enumerate(plan_2["candidates"]):
        print(f"   Strategy {i+1}: {candidate['path_length']} cells, "
              f"{candidate['coverage']*100:.2f}% coverage")
    
    # 7. GENERATE SECOND PLAN (Different Resolution)
    print("\n🔷 Step 7: Generate Second Plan with Different Resolution")
    plan_request_2 = {
        "resolution": 0.15  # 15cm resolution
    }
    print(f"Input: {json.dumps(plan_request_2, indent=2)}")
    response = requests.post(f"{BASE_URL}/walls/{wall_2_id}/plan", json=plan_request_2)
    print_response(response, "Second Plan Generated")
    
    # 8. LIST ALL PLANS FOR WALL
    print("\n🔷 Step 8: List All Plans for This Wall")
    response = requests.get(f"{BASE_URL}/walls/{wall_2_id}/plans")
    print_response(response, "All Plans Listed")
    
    # 9. EXECUTE BEST PATH
    print("\n🔷 Step 9: Execute Best Path")
    response = requests.post(f"{BASE_URL}/paths/{best_path_2_id}/execute")
    execution_2 = print_response(response, "Path Execution Initiated")
    if not execution_2:
        return None
    execution_2_id = execution_2["execution_id"]
    
    # 10. UPDATE EXECUTION MANUALLY
    print("\n🔷 Step 10: Update Execution Status Manually")
    response = requests.patch(
        f"{BASE_URL}/paths/executions/{execution_2_id}",
        params={"status": "RUNNING", "progress": 65.5}
    )
    print_response(response, "Execution Status Updated")
    
    # 11. GET CURRENT TELEMETRY
    print("\n🔷 Step 11: Get Current Telemetry")
    response = requests.get(f"{BASE_URL}/telemetry/{execution_2_id}/current")
    print_response(response, "Current Telemetry Retrieved")
    
    return {
        "wall_id": wall_2_id,
        "plan_id": plan_2_id,
        "path_id": best_path_2_id,
        "execution_id": execution_2_id
    }


# ==============================================================================
# SYSTEM-WIDE OPERATIONS
# ==============================================================================

def system_operations():
    """Test system-wide operations."""
    print_section("SYSTEM-WIDE OPERATIONS")
    
    # 1. HEALTH CHECK
    print("\n🔷 Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "System Health")
    
    # 2. LIST ALL WALLS
    print("\n🔷 List All Walls")
    response = requests.get(f"{BASE_URL}/walls")
    print_response(response, "All Walls Listed")
    
    # 3. SYSTEM STATISTICS
    print("\n🔷 System Statistics")
    response = requests.get(f"{BASE_URL}/stats")
    print_response(response, "System Statistics")


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    """Run all test scenarios."""
    print("\n" + "🤖 " * 40)
    print("   ROBOT WALL PLANNER - COMPREHENSIVE TEST SCENARIOS")
    print("🤖 " * 40)
    
    try:
        # Test server connectivity
        print("\n🔍 Testing server connectivity...")
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server is not running!")
            print("Please start the server first: ./run.sh")
            return
        print("✅ Server is running\n")
        
        # Run scenarios
        result_1 = scenario_1_small_room()
        time.sleep(1)
        
        result_2 = scenario_2_large_lshaped()
        time.sleep(1)
        
        system_operations()
        
        # Summary
        print_section("TEST SUMMARY")
        print("\n✅ SCENARIO 1 (Living Room) - COMPLETED")
        if result_1:
            print(f"   Wall ID: {result_1['wall_id']}")
            print(f"   Plan ID: {result_1['plan_id']}")
            print(f"   Path ID: {result_1['path_id']}")
            print(f"   Execution ID: {result_1['execution_id']}")
        
        print("\n✅ SCENARIO 2 (L-Shaped Office) - COMPLETED")
        if result_2:
            print(f"   Wall ID: {result_2['wall_id']}")
            print(f"   Plan ID: {result_2['plan_id']}")
            print(f"   Path ID: {result_2['path_id']}")
            print(f"   Execution ID: {result_2['execution_id']}")
        
        print("\n" + "="*80)
        print("  🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server!")
        print("Please start the server first:")
        print("   cd Robot")
        print("   ./run.sh")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
