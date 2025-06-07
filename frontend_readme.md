# Frontend Documentation

## Overview
The frontend provides a modern, responsive dashboard interface for the Flask web scraping application.

## Structure
- **templates/index.html** - Main dashboard template
- **static/css/style.css** - Responsive styling with CSS Grid/Flexbox
- **static/js/app.js** - Dynamic functionality and API integration

## Features

### Dashboard Components
1. **Header** - Application title and last update timestamp
2. **Statistics Cards** - Key metrics display:
   - Total Results
   - Success Rate
   - Average Response Time
   - Today's Scrapes

3. **Charts Section** - Data visualizations using Chart.js:
   - Results Over Time (Line Chart)
   - Status Distribution (Doughnut Chart)

4. **Results Table** - Paginated data display with:
   - Search functionality
   - Status filtering
   - Detail view modal
   - 10 results per page

### API Integration
The frontend communicates with these API endpoints:
- `GET /api/results` - Fetch all scraping results
- `GET /api/results/<id>` - Get specific result details
- `GET /api/stats` - Retrieve aggregated statistics

### Responsive Design
- Mobile-first approach
- Breakpoint at 768px
- Flexible grid layouts
- Touch-friendly controls

### Auto-Refresh
Dashboard data automatically refreshes every 30 seconds to show latest results.

## Usage
The frontend is served by Flask at the root URL (`/`). Simply navigate to `http://localhost:5000` after starting the Flask application.