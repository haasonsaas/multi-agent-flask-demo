#!/usr/bin/env python3
"""
Example script demonstrating how to use the Flask Dashboard API
"""
import requests
import json
from datetime import datetime

# API base URL (adjust if running on different host/port)
API_BASE_URL = "http://localhost:5000/api"


def test_get_all_results():
    """Test getting all results"""
    print("\n1. Testing GET /api/results")
    print("-" * 50)
    
    response = requests.get(f"{API_BASE_URL}/results")
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {data['status']}")
        print(f"Total results: {data['total']}")
        print(f"Results returned: {len(data['data'])}")
        
        # Show first result if available
        if data['data']:
            print("\nFirst result:")
            print(json.dumps(data['data'][0], indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def test_get_statistics():
    """Test getting statistics"""
    print("\n2. Testing GET /api/stats")
    print("-" * 50)
    
    response = requests.get(f"{API_BASE_URL}/stats")
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {data['status']}")
        print("\nStatistics:")
        stats = data['data']
        print(f"  Total results: {stats['total_results']}")
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  URLs processed: {stats['total_urls_processed']}")
        print(f"  Agents used: {stats['agents_used']}")
        print(f"  Average content density: {stats['avg_content_density']:.2f}")
        print(f"  Average media ratio: {stats['avg_media_ratio']:.2f}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def test_add_result():
    """Test adding a new result"""
    print("\n3. Testing POST /api/results")
    print("-" * 50)
    
    # Sample data
    new_result = {
        "url": "https://example.com/test",
        "data": {
            "title": "Test Page",
            "text_length": 1500,
            "num_links": 25,
            "num_images": 5,
            "headers": ["Main Header", "Section 1", "Section 2"]
        },
        "analysis": {
            "content_density": 60.0,
            "media_ratio": 0.17,
            "header_count": 3,
            "avg_header_length": 9.33
        },
        "agent_id": 99
    }
    
    response = requests.post(
        f"{API_BASE_URL}/results",
        json=new_result,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"Status: {data['status']}")
        print(f"Message: {data['message']}")
        print("\nCreated result:")
        print(json.dumps(data['data'], indent=2))
        
        # Store the ID for the next test
        return data['data']['id']
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def test_get_result_by_id(result_id):
    """Test getting a specific result by ID"""
    print(f"\n4. Testing GET /api/results/{result_id}")
    print("-" * 50)
    
    response = requests.get(f"{API_BASE_URL}/results/{result_id}")
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {data['status']}")
        print("\nResult details:")
        print(json.dumps(data['data'], indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def test_filters():
    """Test API filters"""
    print("\n5. Testing API filters")
    print("-" * 50)
    
    # Test agent_id filter
    print("\na. Testing agent_id filter (agent_id=1)")
    response = requests.get(f"{API_BASE_URL}/results?agent_id=1")
    if response.status_code == 200:
        data = response.json()
        print(f"Results for agent 1: {len(data['data'])}")
    
    # Test status filter
    print("\nb. Testing status filter (status=success)")
    response = requests.get(f"{API_BASE_URL}/results?status=success")
    if response.status_code == 200:
        data = response.json()
        print(f"Successful results: {len(data['data'])}")
    
    # Test pagination
    print("\nc. Testing pagination (limit=5, offset=0)")
    response = requests.get(f"{API_BASE_URL}/results?limit=5&offset=0")
    if response.status_code == 200:
        data = response.json()
        print(f"Results returned: {len(data['data'])} (limit: {data['limit']}, offset: {data['offset']})")


def main():
    """Run all tests"""
    print("Flask Dashboard API Test Script")
    print("=" * 50)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Testing started at: {datetime.now().isoformat()}")
    
    try:
        # Run tests
        test_get_all_results()
        test_get_statistics()
        result_id = test_add_result()
        
        if result_id:
            test_get_result_by_id(result_id)
        
        test_filters()
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API.")
        print("Make sure the Flask server is running: python app.py")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()