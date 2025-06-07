"""
Pytest configuration and fixtures for Flask dashboard tests.
"""
import os
import sys
import pytest
import tempfile
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config import TestingConfig
from database import Database, init_database
from models import Base, ScrapingResult, AgentStats


@pytest.fixture(scope='session')
def app():
    """Create Flask application instance for testing."""
    app = create_app(TestingConfig)
    app.config['TESTING'] = True
    return app


@pytest.fixture(scope='session')
def client(app):
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture(scope='session')
def runner(app):
    """Create Flask CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db():
    """Create a test database for each test function."""
    # Create a temporary database file
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Initialize database
    test_db = Database(db_path)
    test_db.init_db()
    
    yield test_db
    
    # Cleanup
    test_db.drop_all_tables()
    os.unlink(db_path)


@pytest.fixture
def sample_scraping_result():
    """Sample scraping result data."""
    return {
        'url': 'https://example.com',
        'title': 'Example Domain',
        'text_length': 1500,
        'num_links': 10,
        'num_images': 5,
        'content_density': 0.75,
        'media_ratio': 0.25,
        'header_count': 3,
        'avg_header_length': 15.5,
        'agent_id': 1,
        'headers': ['Welcome', 'About Us', 'Contact'],
        'timestamp': datetime.utcnow()
    }


@pytest.fixture
def sample_scraping_results():
    """Multiple sample scraping results."""
    base_time = datetime.utcnow()
    return [
        {
            'url': 'https://example1.com',
            'title': 'Example 1',
            'text_length': 1000,
            'num_links': 5,
            'num_images': 2,
            'content_density': 0.8,
            'media_ratio': 0.2,
            'header_count': 2,
            'avg_header_length': 10.0,
            'agent_id': 1,
            'headers': ['Header 1', 'Header 2'],
            'timestamp': base_time
        },
        {
            'url': 'https://example2.com',
            'title': 'Example 2',
            'text_length': 2000,
            'num_links': 15,
            'num_images': 8,
            'content_density': 0.6,
            'media_ratio': 0.4,
            'header_count': 4,
            'avg_header_length': 12.5,
            'agent_id': 2,
            'headers': ['Main', 'Section 1', 'Section 2', 'Footer'],
            'timestamp': base_time
        },
        {
            'url': 'https://example3.com',
            'title': 'Example 3',
            'text_length': 500,
            'num_links': 3,
            'num_images': 1,
            'content_density': 0.9,
            'media_ratio': 0.1,
            'header_count': 1,
            'avg_header_length': 8.0,
            'agent_id': 1,
            'headers': ['Welcome'],
            'timestamp': base_time,
            'error': 'Timeout error'
        }
    ]


@pytest.fixture
def populated_db(db, sample_scraping_results):
    """Database populated with sample data."""
    for result_data in sample_scraping_results:
        db.create_scraping_result(result_data)
    
    # Update agent stats
    db.update_agent_stats(1)
    db.update_agent_stats(2)
    
    return db


@pytest.fixture
def api_headers():
    """Common API headers for testing."""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


@pytest.fixture
def invalid_result_data():
    """Invalid scraping result data for testing error cases."""
    return [
        # Missing required field 'url'
        {
            'title': 'No URL',
            'agent_id': 1
        },
        # Missing required field 'agent_id'
        {
            'url': 'https://example.com',
            'title': 'No Agent ID'
        },
        # Invalid data types
        {
            'url': 12345,  # Should be string
            'agent_id': 'not-a-number'  # Should be integer
        },
        # Empty data
        {}
    ]