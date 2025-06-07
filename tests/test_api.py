"""
Unit tests for Flask API endpoints.
"""
import json
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test that health check returns expected response."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'Flask Dashboard API'


class TestResultsEndpoints:
    """Test scraping results endpoints."""
    
    def test_get_all_results_empty(self, client):
        """Test getting results when database is empty."""
        with patch('api.routes.db.get_all_scraping_results', return_value=[]):
            response = client.get('/api/results')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['results'] == []
            assert data['count'] == 0
    
    def test_get_all_results_with_data(self, client, sample_scraping_results):
        """Test getting results when database has data."""
        # Create mock results
        mock_results = []
        for result_data in sample_scraping_results:
            mock_result = MagicMock()
            mock_result.to_dict.return_value = result_data
            mock_results.append(mock_result)
        
        with patch('api.routes.db.get_all_scraping_results', return_value=mock_results):
            response = client.get('/api/results')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['results']) == 3
            assert data['count'] == 3
    
    def test_get_all_results_with_pagination(self, client):
        """Test pagination parameters."""
        mock_results = []
        for i in range(5):
            mock_result = MagicMock()
            mock_result.to_dict.return_value = {'id': i, 'url': f'https://example{i}.com'}
            mock_results.append(mock_result)
        
        with patch('api.routes.db.get_all_scraping_results', return_value=mock_results) as mock_db:
            response = client.get('/api/results?limit=2&offset=1')
            assert response.status_code == 200
            data = json.loads(response.data)
            
            # Verify pagination parameters were passed correctly
            mock_db.assert_called_once_with(limit=2, offset=1)
            assert data['limit'] == 2
            assert data['offset'] == 1
    
    def test_get_all_results_error_handling(self, client):
        """Test error handling in get all results."""
        with patch('api.routes.db.get_all_scraping_results', side_effect=Exception('Database error')):
            response = client.get('/api/results')
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert data['error'] == 'Internal server error'
    
    def test_get_specific_result_success(self, client, sample_scraping_result):
        """Test getting a specific result by ID."""
        mock_result = MagicMock()
        mock_result.to_dict.return_value = sample_scraping_result
        
        with patch('api.routes.db.get_scraping_result', return_value=mock_result):
            response = client.get('/api/results/1')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['url'] == sample_scraping_result['url']
            assert data['title'] == sample_scraping_result['title']
    
    def test_get_specific_result_not_found(self, client):
        """Test getting a non-existent result."""
        with patch('api.routes.db.get_scraping_result', return_value=None):
            response = client.get('/api/results/999')
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
            assert data['error'] == 'Result not found'
    
    def test_get_specific_result_error_handling(self, client):
        """Test error handling when getting specific result."""
        with patch('api.routes.db.get_scraping_result', side_effect=Exception('Database error')):
            response = client.get('/api/results/1')
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert data['error'] == 'Internal server error'
    
    def test_create_result_success(self, client, sample_scraping_result, api_headers):
        """Test creating a new scraping result."""
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {**sample_scraping_result, 'id': 1}
        
        with patch('api.routes.db.create_scraping_result', return_value=mock_result):
            response = client.post(
                '/api/results',
                data=json.dumps(sample_scraping_result),
                headers=api_headers
            )
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['url'] == sample_scraping_result['url']
            assert 'id' in data
    
    def test_create_result_no_data(self, client, api_headers):
        """Test creating result with no data."""
        response = client.post('/api/results', headers=api_headers)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'No data provided'
    
    def test_create_result_missing_required_fields(self, client, api_headers):
        """Test creating result with missing required fields."""
        # Missing 'url'
        response = client.post(
            '/api/results',
            data=json.dumps({'agent_id': 1}),
            headers=api_headers
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'url' in data['error']
        
        # Missing 'agent_id'
        response = client.post(
            '/api/results',
            data=json.dumps({'url': 'https://example.com'}),
            headers=api_headers
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'agent_id' in data['error']
    
    def test_create_result_error_handling(self, client, sample_scraping_result, api_headers):
        """Test error handling when creating result."""
        with patch('api.routes.db.create_scraping_result', side_effect=Exception('Database error')):
            response = client.post(
                '/api/results',
                data=json.dumps(sample_scraping_result),
                headers=api_headers
            )
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert data['error'] == 'Internal server error'


class TestStatsEndpoint:
    """Test statistics endpoint."""
    
    def test_get_stats_success(self, client):
        """Test getting statistics."""
        mock_stats = {
            'total_results': 100,
            'successful_results': 90,
            'failed_results': 10,
            'avg_text_length': 1500.5,
            'avg_links_per_page': 12.3,
            'avg_images_per_page': 5.7,
            'unique_urls': 50,
            'unique_agents': 5
        }
        
        with patch('api.routes.db.get_stats', return_value=mock_stats):
            response = client.get('/api/stats')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['total_results'] == 100
            assert data['successful_results'] == 90
            assert data['failed_results'] == 10
            assert data['avg_text_length'] == 1500.5
    
    def test_get_stats_empty_database(self, client):
        """Test getting statistics from empty database."""
        mock_stats = {
            'total_results': 0,
            'successful_results': 0,
            'failed_results': 0,
            'avg_text_length': 0.0,
            'avg_links_per_page': 0.0,
            'avg_images_per_page': 0.0,
            'unique_urls': 0,
            'unique_agents': 0
        }
        
        with patch('api.routes.db.get_stats', return_value=mock_stats):
            response = client.get('/api/stats')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['total_results'] == 0
            assert all(v == 0 or v == 0.0 for v in data.values())
    
    def test_get_stats_error_handling(self, client):
        """Test error handling when getting stats."""
        with patch('api.routes.db.get_stats', side_effect=Exception('Database error')):
            response = client.get('/api/stats')
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert data['error'] == 'Internal server error'


class TestCORSHeaders:
    """Test CORS configuration."""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.get('/api/results')
        assert 'Access-Control-Allow-Origin' in response.headers
        
        # Test preflight request
        response = client.options('/api/results')
        assert response.status_code == 200
        assert 'Access-Control-Allow-Methods' in response.headers


class TestErrorScenarios:
    """Test various error scenarios."""
    
    def test_invalid_endpoint(self, client):
        """Test accessing non-existent endpoint."""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
    
    def test_invalid_http_method(self, client):
        """Test using invalid HTTP method."""
        response = client.delete('/api/results')
        assert response.status_code == 405
    
    def test_malformed_json(self, client, api_headers):
        """Test sending malformed JSON."""
        response = client.post(
            '/api/results',
            data='{"invalid": json}',
            headers=api_headers
        )
        assert response.status_code == 400
    
    def test_invalid_content_type(self, client):
        """Test sending data with wrong content type."""
        response = client.post(
            '/api/results',
            data='url=test&agent_id=1',
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        # Should still work as Flask can handle form data
        assert response.status_code in [400, 415]