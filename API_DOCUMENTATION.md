# Flask Dashboard API Documentation

## Overview

The Flask Dashboard API provides endpoints for managing and retrieving web scraping results. All API endpoints return JSON responses and follow RESTful conventions.

## Base URL

```
http://localhost:5000/api
```

## Response Format

All successful responses follow this general structure:

```json
{
    "data": {...},  // or array for list endpoints
    "status": "success"
}
```

Error responses follow this structure:

```json
{
    "error": "Error message",
    "status": "error"
}
```

## Endpoints

### Health Check

Check if the API service is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
    "status": "healthy",
    "service": "Flask Dashboard API"
}
```

**Example:**
```bash
curl http://localhost:5000/health
```

---

### Get All Scraping Results

Retrieve all scraping results with optional pagination.

**Endpoint:** `GET /api/results`

**Query Parameters:**
- `limit` (optional): Number of results to return
- `offset` (optional): Number of results to skip (default: 0)

**Response:**
```json
{
    "results": [
        {
            "id": 1,
            "url": "https://example.com",
            "title": "Example Domain",
            "text_length": 1500,
            "num_links": 10,
            "num_images": 5,
            "content_density": 0.75,
            "media_ratio": 0.25,
            "header_count": 3,
            "avg_header_length": 15.5,
            "timestamp": "2025-06-06T12:00:00",
            "agent_id": 1,
            "headers": ["Welcome", "About Us", "Contact"],
            "error": null
        }
    ],
    "count": 1,
    "limit": null,
    "offset": 0
}
```

**Examples:**
```bash
# Get all results
curl http://localhost:5000/api/results

# Get paginated results
curl "http://localhost:5000/api/results?limit=10&offset=20"
```

---

### Get Specific Scraping Result

Retrieve a single scraping result by ID.

**Endpoint:** `GET /api/results/<id>`

**URL Parameters:**
- `id`: The unique identifier of the scraping result

**Response:**
```json
{
    "id": 1,
    "url": "https://example.com",
    "title": "Example Domain",
    "text_length": 1500,
    "num_links": 10,
    "num_images": 5,
    "content_density": 0.75,
    "media_ratio": 0.25,
    "header_count": 3,
    "avg_header_length": 15.5,
    "timestamp": "2025-06-06T12:00:00",
    "agent_id": 1,
    "headers": ["Welcome", "About Us", "Contact"],
    "error": null
}
```

**Error Response (404):**
```json
{
    "error": "Result not found"
}
```

**Example:**
```bash
curl http://localhost:5000/api/results/1
```

---

### Create New Scraping Result

Add a new scraping result to the database.

**Endpoint:** `POST /api/results`

**Headers:**
- `Content-Type: application/json`

**Request Body:**
```json
{
    "url": "https://example.com",
    "agent_id": 1,
    "title": "Example Domain",
    "text_length": 1500,
    "num_links": 10,
    "num_images": 5,
    "content_density": 0.75,
    "media_ratio": 0.25,
    "header_count": 3,
    "avg_header_length": 15.5,
    "headers": ["Welcome", "About Us", "Contact"]
}
```

**Required Fields:**
- `url`: The URL that was scraped
- `agent_id`: The ID of the agent that performed the scraping

**Optional Fields:**
- `title`: Page title
- `text_length`: Total length of text content
- `num_links`: Number of links found
- `num_images`: Number of images found
- `content_density`: Ratio of text to HTML
- `media_ratio`: Ratio of media elements
- `header_count`: Number of headers
- `avg_header_length`: Average length of headers
- `headers`: Array of header texts
- `error`: Error message if scraping failed

**Response (201):**
```json
{
    "id": 1,
    "url": "https://example.com",
    "title": "Example Domain",
    "text_length": 1500,
    "num_links": 10,
    "num_images": 5,
    "content_density": 0.75,
    "media_ratio": 0.25,
    "header_count": 3,
    "avg_header_length": 15.5,
    "timestamp": "2025-06-06T12:00:00",
    "agent_id": 1,
    "headers": ["Welcome", "About Us", "Contact"],
    "error": null
}
```

**Error Responses:**

400 Bad Request - No data provided:
```json
{
    "error": "No data provided"
}
```

400 Bad Request - Missing required field:
```json
{
    "error": "Missing required field: url"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/results \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "agent_id": 1,
    "title": "Example Domain",
    "text_length": 1500,
    "num_links": 10,
    "num_images": 5
  }'
```

---

### Get Aggregated Statistics

Retrieve aggregated statistics from all scraping results.

**Endpoint:** `GET /api/stats`

**Response:**
```json
{
    "total_results": 100,
    "successful_results": 90,
    "failed_results": 10,
    "avg_text_length": 1500.5,
    "avg_links_per_page": 12.3,
    "avg_images_per_page": 5.7,
    "unique_urls": 50,
    "unique_agents": 5
}
```

**Fields:**
- `total_results`: Total number of scraping results
- `successful_results`: Number of successful scrapes (no errors)
- `failed_results`: Number of failed scrapes (with errors)
- `avg_text_length`: Average text length across successful scrapes
- `avg_links_per_page`: Average number of links per page
- `avg_images_per_page`: Average number of images per page
- `unique_urls`: Number of unique URLs scraped
- `unique_agents`: Number of unique agents that have submitted results

**Example:**
```bash
curl http://localhost:5000/api/stats
```

---

## Error Codes

The API uses standard HTTP status codes:

- `200 OK`: Successful GET request
- `201 Created`: Successful POST request that created a resource
- `400 Bad Request`: Invalid request data or missing required fields
- `404 Not Found`: Requested resource not found
- `405 Method Not Allowed`: HTTP method not supported for endpoint
- `500 Internal Server Error`: Server-side error

---

## CORS Support

The API has CORS enabled for all origins on `/api/*` endpoints. This allows frontend applications from different domains to access the API.

---

## Data Models

### ScrapingResult

Represents a single web scraping result.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | auto | Unique identifier |
| url | string | yes | URL that was scraped |
| agent_id | integer | yes | ID of the scraping agent |
| title | string | no | Page title |
| text_length | integer | no | Total text content length |
| num_links | integer | no | Number of links found |
| num_images | integer | no | Number of images found |
| content_density | float | no | Text to HTML ratio |
| media_ratio | float | no | Media elements ratio |
| header_count | integer | no | Number of headers |
| avg_header_length | float | no | Average header length |
| headers | array | no | List of header texts |
| timestamp | datetime | auto | When the result was created |
| error | string | no | Error message if scraping failed |

---

## Examples

### Complete Workflow Example

```bash
# 1. Check API health
curl http://localhost:5000/health

# 2. Create a new scraping result
curl -X POST http://localhost:5000/api/results \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "agent_id": 1,
    "title": "Example Domain",
    "text_length": 1500,
    "num_links": 10,
    "num_images": 5,
    "content_density": 0.75,
    "media_ratio": 0.25,
    "header_count": 3,
    "avg_header_length": 15.5,
    "headers": ["Welcome", "About Us", "Contact"]
  }'

# 3. Get all results
curl http://localhost:5000/api/results

# 4. Get specific result (assuming ID 1)
curl http://localhost:5000/api/results/1

# 5. Get statistics
curl http://localhost:5000/api/stats

# 6. Get paginated results
curl "http://localhost:5000/api/results?limit=5&offset=0"
```

### Error Handling Example

```bash
# Missing required field
curl -X POST http://localhost:5000/api/results \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Missing URL field"
  }'
# Returns: {"error": "Missing required field: url"}

# Non-existent resource
curl http://localhost:5000/api/results/999999
# Returns: {"error": "Result not found"}
```

### Using with JavaScript (Fetch API)

```javascript
// Get all results
fetch('http://localhost:5000/api/results')
  .then(response => response.json())
  .then(data => console.log(data));

// Create new result
fetch('http://localhost:5000/api/results', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'https://example.com',
    agent_id: 1,
    title: 'Example Domain'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

### Using with Python (requests)

```python
import requests

# Get all results
response = requests.get('http://localhost:5000/api/results')
print(response.json())

# Create new result
data = {
    'url': 'https://example.com',
    'agent_id': 1,
    'title': 'Example Domain'
}
response = requests.post('http://localhost:5000/api/results', json=data)
print(response.json())
```