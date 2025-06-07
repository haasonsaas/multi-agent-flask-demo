# Flask Dashboard API Documentation

## Overview
This Flask API provides endpoints for managing and retrieving web scraping results from the data_processor.py module.

## Setup

### Installation
```bash
pip install -r requirements.txt
```

### Running the Server
```bash
python app.py
```

The server will start on `http://localhost:5000` by default.

## API Endpoints

### 1. Get All Results
**GET** `/api/results`

Retrieves all scraping results with optional filtering and pagination.

#### Query Parameters:
- `limit` (integer, default: 100): Maximum number of results to return
- `offset` (integer, default: 0): Number of results to skip
- `agent_id` (integer): Filter by specific agent ID
- `status` (string): Filter by status ('success' or 'error')

#### Example Request:
```bash
curl "http://localhost:5000/api/results?limit=10&agent_id=1&status=success"
```

#### Example Response:
```json
{
  "status": "success",
  "data": [
    {
      "id": "results_20231201_120000.json_0",
      "url": "https://example.com",
      "timestamp": "2023-12-01T12:00:00",
      "agent_id": 1,
      "data": {
        "title": "Example Domain",
        "text_length": 1256,
        "num_links": 2,
        "num_images": 0,
        "headers": ["Example Domain"]
      },
      "analysis": {
        "content_density": 628.0,
        "media_ratio": 0.0,
        "header_count": 1,
        "avg_header_length": 14.0
      }
    }
  ],
  "total": 50,
  "limit": 10,
  "offset": 0
}
```

### 2. Get Result by ID
**GET** `/api/results/<id>`

Retrieves a specific result by its ID.

#### Example Request:
```bash
curl "http://localhost:5000/api/results/results_20231201_120000.json_0"
```

#### Example Response:
```json
{
  "status": "success",
  "data": {
    "id": "results_20231201_120000.json_0",
    "url": "https://example.com",
    "timestamp": "2023-12-01T12:00:00",
    "agent_id": 1,
    "data": {...},
    "analysis": {...}
  }
}
```

### 3. Get Statistics
**GET** `/api/stats`

Returns aggregated statistics from all scraping results.

#### Example Request:
```bash
curl "http://localhost:5000/api/stats"
```

#### Example Response:
```json
{
  "status": "success",
  "data": {
    "total_results": 100,
    "successful_results": 95,
    "failed_results": 5,
    "success_rate": 95.0,
    "total_urls_processed": 50,
    "agents_used": [1, 2, 3],
    "processing_dates": ["2023-12-01", "2023-12-02"],
    "avg_content_density": 450.5,
    "avg_media_ratio": 0.25,
    "total_links_found": 1250,
    "total_images_found": 300,
    "url_statistics": {
      "https://example.com": {
        "success": 5,
        "failed": 1
      }
    }
  }
}
```

### 4. Add New Result
**POST** `/api/results`

Adds a new scraping result to the system.

#### Request Headers:
```
Content-Type: application/json
```

#### Request Body:
```json
{
  "url": "https://example.com",
  "data": {
    "title": "Example Page",
    "text_length": 1500,
    "num_links": 25,
    "num_images": 5,
    "headers": ["Main Header", "Section 1"]
  },
  "analysis": {
    "content_density": 60.0,
    "media_ratio": 0.17,
    "header_count": 2,
    "avg_header_length": 10.5
  },
  "agent_id": 1
}
```

#### Example Request:
```bash
curl -X POST "http://localhost:5000/api/results" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "agent_id": 1,
    "data": {
      "title": "Test",
      "text_length": 1000,
      "num_links": 10,
      "num_images": 2,
      "headers": []
    }
  }'
```

#### Example Response:
```json
{
  "status": "success",
  "message": "Result added successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "url": "https://example.com",
    "timestamp": "2023-12-01T15:30:00",
    "agent_id": 1,
    "data": {...}
  }
}
```

### 5. Health Check
**GET** `/health`

Check if the API is running.

#### Example Request:
```bash
curl "http://localhost:5000/health"
```

#### Example Response:
```json
{
  "status": "healthy",
  "service": "Flask Dashboard API"
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "status": "error",
  "message": "Description of the error",
  "error": "Detailed error message (optional)"
}
```

Common HTTP status codes:
- 200: Success
- 201: Created (for POST requests)
- 400: Bad Request (invalid input)
- 404: Not Found
- 500: Internal Server Error

## CORS Support

The API supports Cross-Origin Resource Sharing (CORS) for all `/api/*` endpoints, allowing requests from any origin. This enables the frontend to communicate with the API from different domains.

## Configuration

The API can be configured using environment variables:

- `PORT`: Server port (default: 5000)
- `FLASK_DEBUG`: Enable debug mode (default: True)
- `SECRET_KEY`: Flask secret key
- `RESULTS_DIR`: Directory containing result files (default: 'results')
- `LOG_LEVEL`: Logging level (default: 'INFO')

## Testing the API

Use the provided `example_api_usage.py` script to test all endpoints:

```bash
python example_api_usage.py
```

This script demonstrates how to interact with each endpoint and can serve as a reference for integration.