# Database Module Documentation

This module provides the data models and database layer for the Flask dashboard project.

## Files Created

### 1. `models.py`
Contains SQLAlchemy models:
- **ScrapingResult**: Stores web scraping results with fields matching the data_processor.py output
- **AgentStats**: Stores aggregated statistics per agent

### 2. `database.py`
Provides database operations:
- Database initialization and connection management
- CRUD operations for all models
- Bulk operations for efficient data insertion
- Statistics and aggregation functions
- Search functionality

### 3. `migrate_data.py`
Migration script to:
- Find and parse JSON files from data_processor.py
- Transform data to match database schema
- Migrate data to SQLite database
- Generate sample data for testing
- Update agent statistics

### 4. `test_database.py`
Test script to verify all database operations work correctly.

## Usage

### Initialize Database
```python
from database import init_database
db = init_database("dashboard.db")
```

### Migrate Existing Data
```bash
# Migrate all JSON files from results directory
python migrate_data.py

# Generate sample data if no results exist
python migrate_data.py --generate-sample

# Reset database (warning: deletes all data)
python migrate_data.py --reset-db
```

### Basic Operations
```python
from database import Database

db = Database("dashboard.db")

# Create a result
result = db.create_scraping_result({
    'url': 'https://example.com',
    'title': 'Example',
    'text_length': 1000,
    'agent_id': 1
})

# Get statistics
stats = db.get_stats()
agent_stats = db.get_agent_stats(1)

# Search results
results = db.search_results("example")
```

## Database Schema

### ScrapingResult Table
- `id`: Primary key
- `url`: URL that was scraped
- `title`: Page title
- `text_length`: Length of text content
- `num_links`: Number of links found
- `num_images`: Number of images found
- `content_density`: Calculated content density
- `media_ratio`: Ratio of media to content
- `header_count`: Number of headers
- `avg_header_length`: Average header length
- `timestamp`: When the scraping occurred
- `agent_id`: ID of the agent that performed the scrape
- `headers`: JSON array of headers
- `error`: Error message if scraping failed

### AgentStats Table
- `id`: Primary key
- `agent_id`: Unique agent identifier
- `total_urls_processed`: Total URLs processed by agent
- `successful_scrapes`: Number of successful scrapes
- `failed_scrapes`: Number of failed scrapes
- `avg_text_length`: Average text length of successful scrapes
- `avg_links_per_page`: Average links per page
- `avg_images_per_page`: Average images per page
- `last_updated`: Last update timestamp

## Indexes
- `idx_agent_timestamp`: Composite index on agent_id and timestamp
- `idx_url`: Index on URL for fast lookups
- `idx_timestamp`: Index on timestamp for recent results queries

## Testing
Run the test script to verify functionality:
```bash
python test_database.py
```