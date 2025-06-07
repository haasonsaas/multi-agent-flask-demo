"""
Test script to verify database functionality.
"""
from datetime import datetime
from database import Database, init_database
from models import ScrapingResult, AgentStats


def test_database():
    """Test basic database operations."""
    print("Testing database functionality...")
    
    # Initialize database
    db = init_database("test_dashboard.db")
    
    # Test 1: Create a scraping result
    print("\n1. Testing create operation...")
    test_data = {
        'url': 'https://example.com',
        'title': 'Example Domain',
        'text_length': 1500,
        'num_links': 10,
        'num_images': 3,
        'content_density': 150.0,
        'media_ratio': 0.23,
        'header_count': 5,
        'avg_header_length': 12.5,
        'agent_id': 1,
        'headers': ['Welcome', 'About Us', 'Services', 'Contact', 'Footer']
    }
    
    result = db.create_scraping_result(test_data)
    print(f"Created result with ID: {result.id}")
    
    # Test 2: Read the result
    print("\n2. Testing read operation...")
    fetched = db.get_scraping_result(result.id)
    print(f"Fetched result: {fetched.to_dict()}")
    
    # Test 3: Update the result
    print("\n3. Testing update operation...")
    update_data = {'title': 'Updated Example Domain', 'num_links': 15}
    updated = db.update_scraping_result(result.id, update_data)
    print(f"Updated title: {updated.title}, links: {updated.num_links}")
    
    # Test 4: Create multiple results
    print("\n4. Testing bulk create...")
    bulk_data = [
        {
            'url': f'https://test{i}.com',
            'title': f'Test Site {i}',
            'text_length': 1000 + i * 100,
            'num_links': 5 + i,
            'num_images': 2 + i,
            'agent_id': i % 3 + 1,
            'content_density': 100.0 + i * 10,
            'media_ratio': 0.1 + i * 0.05
        }
        for i in range(5)
    ]
    
    bulk_results = db.bulk_create_scraping_results(bulk_data)
    print(f"Created {len(bulk_results)} bulk results")
    
    # Test 5: Query operations
    print("\n5. Testing query operations...")
    
    # Get all results
    all_results = db.get_all_scraping_results()
    print(f"Total results in database: {len(all_results)}")
    
    # Get results by agent
    agent_results = db.get_results_by_agent(1)
    print(f"Results for agent 1: {len(agent_results)}")
    
    # Get recent results
    recent = db.get_recent_results(limit=3)
    print(f"Recent results: {len(recent)}")
    
    # Test 6: Statistics
    print("\n6. Testing statistics...")
    stats = db.get_stats()
    print(f"Overall stats: {stats}")
    
    agent_stats = db.get_agent_stats(1)
    print(f"Agent 1 stats: {agent_stats}")
    
    # Test 7: Search
    print("\n7. Testing search...")
    search_results = db.search_results("example")
    print(f"Search results for 'example': {len(search_results)}")
    
    # Test 8: Error handling
    print("\n8. Testing error result...")
    error_data = {
        'url': 'https://error.com',
        'agent_id': 2,
        'error': 'Connection timeout after 10 seconds'
    }
    error_result = db.create_scraping_result(error_data)
    print(f"Created error result with ID: {error_result.id}")
    
    # Test 9: Agent stats update
    print("\n9. Testing agent stats update...")
    db.update_agent_stats(1)
    db.update_agent_stats(2)
    
    with db.get_session() as session:
        agent_stats = session.query(AgentStats).all()
        print(f"Agent stats records: {len(agent_stats)}")
        for stat in agent_stats:
            print(f"  Agent {stat.agent_id}: {stat.total_urls_processed} URLs, "
                  f"{stat.successful_scrapes} successful, {stat.failed_scrapes} failed")
    
    # Test 10: Delete operation
    print("\n10. Testing delete operation...")
    deleted = db.delete_scraping_result(result.id)
    print(f"Delete successful: {deleted}")
    
    # Verify deletion
    deleted_result = db.get_scraping_result(result.id)
    print(f"Result after deletion: {deleted_result}")
    
    print("\n✅ All tests completed successfully!")
    
    # Clean up test database
    import os
    os.remove("test_dashboard.db")
    print("Test database cleaned up.")


if __name__ == "__main__":
    test_database()