"""
Unit tests for database models and operations.
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from models import ScrapingResult, AgentStats


class TestScrapingResultModel:
    """Test ScrapingResult model."""
    
    def test_create_scraping_result(self, db, sample_scraping_result):
        """Test creating a scraping result."""
        result = db.create_scraping_result(sample_scraping_result)
        
        assert result.id is not None
        assert result.url == sample_scraping_result['url']
        assert result.title == sample_scraping_result['title']
        assert result.agent_id == sample_scraping_result['agent_id']
        assert result.text_length == sample_scraping_result['text_length']
        assert result.headers == sample_scraping_result['headers']
    
    def test_scraping_result_defaults(self, db):
        """Test default values for scraping result."""
        minimal_data = {
            'url': 'https://test.com',
            'agent_id': 1
        }
        result = db.create_scraping_result(minimal_data)
        
        assert result.text_length == 0
        assert result.num_links == 0
        assert result.num_images == 0
        assert result.content_density == 0.0
        assert result.media_ratio == 0.0
        assert result.header_count == 0
        assert result.avg_header_length == 0.0
        assert result.error is None
    
    def test_scraping_result_to_dict(self, db, sample_scraping_result):
        """Test converting scraping result to dictionary."""
        result = db.create_scraping_result(sample_scraping_result)
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['id'] == result.id
        assert result_dict['url'] == result.url
        assert result_dict['title'] == result.title
        assert result_dict['agent_id'] == result.agent_id
        assert 'timestamp' in result_dict
        assert isinstance(result_dict['timestamp'], str)  # ISO format string
    
    def test_scraping_result_with_error(self, db):
        """Test creating scraping result with error."""
        data = {
            'url': 'https://error.com',
            'agent_id': 1,
            'error': 'Connection timeout'
        }
        result = db.create_scraping_result(data)
        
        assert result.error == 'Connection timeout'
        assert result.to_dict()['error'] == 'Connection timeout'
    
    def test_scraping_result_repr(self, db, sample_scraping_result):
        """Test string representation of scraping result."""
        result = db.create_scraping_result(sample_scraping_result)
        repr_str = repr(result)
        
        assert f"id={result.id}" in repr_str
        assert f"url='{result.url}'" in repr_str
        assert f"agent_id={result.agent_id}" in repr_str


class TestAgentStatsModel:
    """Test AgentStats model."""
    
    def test_create_agent_stats(self, db):
        """Test creating agent statistics."""
        with db.get_session() as session:
            stats = AgentStats(
                agent_id=1,
                total_urls_processed=10,
                successful_scrapes=9,
                failed_scrapes=1,
                avg_text_length=1500.5,
                avg_links_per_page=10.2,
                avg_images_per_page=5.5
            )
            session.add(stats)
            session.flush()
            
            assert stats.id is not None
            assert stats.agent_id == 1
            assert stats.total_urls_processed == 10
            assert stats.successful_scrapes == 9
            assert stats.failed_scrapes == 1
    
    def test_agent_stats_to_dict(self, db):
        """Test converting agent stats to dictionary."""
        with db.get_session() as session:
            stats = AgentStats(agent_id=2)
            session.add(stats)
            session.flush()
            
            stats_dict = stats.to_dict()
            assert isinstance(stats_dict, dict)
            assert stats_dict['agent_id'] == 2
            assert 'last_updated' in stats_dict
    
    def test_agent_stats_unique_constraint(self, db):
        """Test that agent_id is unique in agent stats."""
        # Create first stats entry
        with db.get_session() as session:
            stats1 = AgentStats(agent_id=1)
            session.add(stats1)
        
        # Try to create duplicate
        with pytest.raises(IntegrityError):
            with db.get_session() as session:
                stats2 = AgentStats(agent_id=1)
                session.add(stats2)


class TestDatabaseOperations:
    """Test database CRUD operations."""
    
    def test_get_scraping_result_by_id(self, db, sample_scraping_result):
        """Test retrieving scraping result by ID."""
        created = db.create_scraping_result(sample_scraping_result)
        retrieved = db.get_scraping_result(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.url == created.url
    
    def test_get_nonexistent_result(self, db):
        """Test retrieving non-existent result."""
        result = db.get_scraping_result(999)
        assert result is None
    
    def test_get_all_scraping_results(self, populated_db):
        """Test retrieving all scraping results."""
        results = populated_db.get_all_scraping_results()
        assert len(results) == 3
        # Results should be ordered by timestamp desc
        assert all(results[i].timestamp >= results[i+1].timestamp 
                  for i in range(len(results)-1))
    
    def test_get_all_results_with_pagination(self, populated_db):
        """Test pagination of results."""
        # Get first page
        page1 = populated_db.get_all_scraping_results(limit=2, offset=0)
        assert len(page1) == 2
        
        # Get second page
        page2 = populated_db.get_all_scraping_results(limit=2, offset=2)
        assert len(page2) == 1
        
        # Verify no overlap
        page1_ids = [r.id for r in page1]
        page2_ids = [r.id for r in page2]
        assert not set(page1_ids).intersection(set(page2_ids))
    
    def test_get_results_by_agent(self, populated_db):
        """Test retrieving results by agent ID."""
        agent1_results = populated_db.get_results_by_agent(1)
        agent2_results = populated_db.get_results_by_agent(2)
        
        assert len(agent1_results) == 2
        assert len(agent2_results) == 1
        assert all(r.agent_id == 1 for r in agent1_results)
        assert all(r.agent_id == 2 for r in agent2_results)
    
    def test_get_results_by_url(self, populated_db):
        """Test retrieving results by URL."""
        results = populated_db.get_results_by_url('https://example1.com')
        assert len(results) == 1
        assert results[0].url == 'https://example1.com'
    
    def test_update_scraping_result(self, db, sample_scraping_result):
        """Test updating a scraping result."""
        result = db.create_scraping_result(sample_scraping_result)
        original_title = result.title
        
        updated = db.update_scraping_result(
            result.id,
            {'title': 'Updated Title', 'num_links': 20}
        )
        
        assert updated is not None
        assert updated.title == 'Updated Title'
        assert updated.num_links == 20
        assert updated.url == sample_scraping_result['url']  # Unchanged
    
    def test_update_nonexistent_result(self, db):
        """Test updating non-existent result."""
        updated = db.update_scraping_result(999, {'title': 'New Title'})
        assert updated is None
    
    def test_delete_scraping_result(self, db, sample_scraping_result):
        """Test deleting a scraping result."""
        result = db.create_scraping_result(sample_scraping_result)
        result_id = result.id
        
        # Delete the result
        deleted = db.delete_scraping_result(result_id)
        assert deleted is True
        
        # Verify it's gone
        retrieved = db.get_scraping_result(result_id)
        assert retrieved is None
    
    def test_delete_nonexistent_result(self, db):
        """Test deleting non-existent result."""
        deleted = db.delete_scraping_result(999)
        assert deleted is False
    
    def test_bulk_create_scraping_results(self, db, sample_scraping_results):
        """Test bulk creation of scraping results."""
        results = db.bulk_create_scraping_results(sample_scraping_results)
        
        assert len(results) == len(sample_scraping_results)
        all_results = db.get_all_scraping_results()
        assert len(all_results) == len(sample_scraping_results)


class TestStatisticsOperations:
    """Test statistics and aggregation operations."""
    
    def test_get_overall_stats(self, populated_db):
        """Test getting overall statistics."""
        stats = populated_db.get_stats()
        
        assert stats['total_results'] == 3
        assert stats['successful_results'] == 2  # One has error
        assert stats['failed_results'] == 1
        assert stats['unique_urls'] == 3
        assert stats['unique_agents'] == 2
        assert stats['avg_text_length'] > 0
        assert stats['avg_links_per_page'] > 0
        assert stats['avg_images_per_page'] > 0
    
    def test_get_stats_empty_database(self, db):
        """Test getting stats from empty database."""
        stats = db.get_stats()
        
        assert stats['total_results'] == 0
        assert stats['successful_results'] == 0
        assert stats['failed_results'] == 0
        assert stats['avg_text_length'] == 0.0
    
    def test_get_agent_stats(self, populated_db):
        """Test getting statistics for specific agent."""
        stats = populated_db.get_agent_stats(1)
        
        assert stats['agent_id'] == 1
        assert stats['total_urls_processed'] == 2
        assert stats['successful_scrapes'] == 1  # One has error
        assert stats['failed_scrapes'] == 1
        assert stats['avg_text_length'] > 0
    
    def test_get_agent_stats_no_results(self, db):
        """Test getting stats for agent with no results."""
        stats = db.get_agent_stats(999)
        
        assert stats['agent_id'] == 999
        assert stats['total_urls_processed'] == 0
        assert all(v == 0 or v == 0.0 for k, v in stats.items() if k != 'agent_id')
    
    def test_update_agent_stats(self, populated_db):
        """Test updating agent statistics."""
        # Stats should already be updated in populated_db fixture
        with populated_db.get_session() as session:
            agent_stat = session.query(AgentStats).filter(
                AgentStats.agent_id == 1
            ).first()
            
            assert agent_stat is not None
            assert agent_stat.total_urls_processed == 2
            assert agent_stat.successful_scrapes == 1
            assert agent_stat.failed_scrapes == 1
    
    def test_get_recent_results(self, db):
        """Test getting recent results."""
        # Create results with different timestamps
        base_time = datetime.utcnow()
        for i in range(15):
            db.create_scraping_result({
                'url': f'https://example{i}.com',
                'agent_id': 1,
                'timestamp': base_time - timedelta(hours=i)
            })
        
        recent = db.get_recent_results(limit=10)
        assert len(recent) == 10
        
        # Verify ordering (most recent first)
        for i in range(len(recent) - 1):
            assert recent[i].timestamp >= recent[i + 1].timestamp
    
    def test_search_results(self, populated_db):
        """Test searching results by URL or title."""
        # Search by URL
        results = populated_db.search_results('example1')
        assert len(results) == 1
        assert 'example1' in results[0].url
        
        # Search by title
        results = populated_db.search_results('Example 2')
        assert len(results) == 1
        assert results[0].title == 'Example 2'
        
        # Search with no matches
        results = populated_db.search_results('nonexistent')
        assert len(results) == 0


class TestDatabaseIntegrity:
    """Test database integrity and constraints."""
    
    def test_required_fields(self, db):
        """Test that required fields are enforced."""
        # Missing URL
        with pytest.raises(Exception):
            db.create_scraping_result({'agent_id': 1})
        
        # Missing agent_id
        with pytest.raises(Exception):
            db.create_scraping_result({'url': 'https://test.com'})
    
    def test_indexes_exist(self, db):
        """Test that indexes are created properly."""
        # This test verifies indexes are created by checking the schema
        with db.get_session() as session:
            # Get table info
            result = session.execute(
                "SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='scraping_results'"
            )
            indexes = [row[0] for row in result if row[0]]
            
            # Verify our custom indexes exist
            assert any('idx_agent_timestamp' in idx for idx in indexes)
            assert any('idx_url' in idx for idx in indexes)
            assert any('idx_timestamp' in idx for idx in indexes)