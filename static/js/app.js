// Global variables
let currentPage = 1;
const itemsPerPage = 10;
let allResults = [];
let filteredResults = [];
let timeChart = null;
let statusChart = null;

// API endpoints
const API_BASE = '/api';
const ENDPOINTS = {
    results: `${API_BASE}/results`,
    stats: `${API_BASE}/stats`
};

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
    loadDashboardData();
    setupEventListeners();
    
    // Refresh data every 30 seconds
    setInterval(loadDashboardData, 30000);
});

// Setup event listeners
function setupEventListeners() {
    // Search input
    document.getElementById('search-input').addEventListener('input', (e) => {
        filterResults();
    });
    
    // Status filter
    document.getElementById('filter-status').addEventListener('change', (e) => {
        filterResults();
    });
    
    // Pagination
    document.getElementById('prev-page').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            displayResults();
        }
    });
    
    document.getElementById('next-page').addEventListener('click', () => {
        const totalPages = Math.ceil(filteredResults.length / itemsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            displayResults();
        }
    });
    
    // Modal close
    document.querySelector('.close').addEventListener('click', () => {
        document.getElementById('result-modal').style.display = 'none';
    });
    
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('result-modal');
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Load all dashboard data
async function loadDashboardData() {
    try {
        // Load statistics
        await loadStatistics();
        
        // Load results
        await loadResults();
        
        // Update timestamp
        updateTimestamp();
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError('Failed to load dashboard data');
    }
}

// Load statistics
async function loadStatistics() {
    try {
        const response = await fetch(ENDPOINTS.stats);
        if (!response.ok) throw new Error('Failed to load statistics');
        
        const stats = await response.json();
        
        // Update stat cards
        document.getElementById('total-results').textContent = stats.total_results || 0;
        document.getElementById('success-rate').textContent = `${stats.success_rate || 0}%`;
        document.getElementById('avg-response-time').textContent = `${stats.avg_response_time || 0}ms`;
        document.getElementById('today-scrapes').textContent = stats.today_scrapes || 0;
        
        // Update charts
        updateCharts(stats);
    } catch (error) {
        console.error('Error loading statistics:', error);
        // Set default values on error
        document.getElementById('total-results').textContent = '0';
        document.getElementById('success-rate').textContent = '0%';
        document.getElementById('avg-response-time').textContent = '0ms';
        document.getElementById('today-scrapes').textContent = '0';
    }
}

// Load results
async function loadResults() {
    try {
        const response = await fetch(ENDPOINTS.results);
        if (!response.ok) throw new Error('Failed to load results');
        
        const data = await response.json();
        allResults = data.results || [];
        filterResults();
    } catch (error) {
        console.error('Error loading results:', error);
        allResults = [];
        filterResults();
    }
}

// Filter results based on search and status
function filterResults() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const statusFilter = document.getElementById('filter-status').value;
    
    filteredResults = allResults.filter(result => {
        const matchesSearch = !searchTerm || 
            result.url.toLowerCase().includes(searchTerm) ||
            result.id.toString().includes(searchTerm);
            
        const matchesStatus = !statusFilter || result.status === statusFilter;
        
        return matchesSearch && matchesStatus;
    });
    
    currentPage = 1;
    displayResults();
}

// Display results in table
function displayResults() {
    const tbody = document.getElementById('results-tbody');
    tbody.innerHTML = '';
    
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageResults = filteredResults.slice(startIndex, endIndex);
    
    if (pageResults.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px;">No results found</td></tr>';
    } else {
        pageResults.forEach(result => {
            const row = createResultRow(result);
            tbody.appendChild(row);
        });
    }
    
    updatePagination();
}

// Create a result row
function createResultRow(result) {
    const row = document.createElement('tr');
    
    // Format timestamp
    const timestamp = new Date(result.timestamp).toLocaleString();
    
    // Create status badge
    const statusClass = `status-${result.status}`;
    const statusBadge = `<span class="status-badge ${statusClass}">${result.status}</span>`;
    
    row.innerHTML = `
        <td>${result.id}</td>
        <td>${truncateUrl(result.url, 50)}</td>
        <td>${statusBadge}</td>
        <td>${result.response_time || 0}ms</td>
        <td>${timestamp}</td>
        <td>
            <button class="action-btn" onclick="viewDetails(${result.id})">View</button>
        </td>
    `;
    
    return row;
}

// Truncate URL for display
function truncateUrl(url, maxLength) {
    if (url.length <= maxLength) return url;
    return url.substring(0, maxLength) + '...';
}

// Update pagination controls
function updatePagination() {
    const totalPages = Math.ceil(filteredResults.length / itemsPerPage);
    
    // Update page info
    document.getElementById('page-info').textContent = `Page ${currentPage} of ${totalPages || 1}`;
    
    // Update button states
    document.getElementById('prev-page').disabled = currentPage === 1;
    document.getElementById('next-page').disabled = currentPage >= totalPages;
}

// View result details
async function viewDetails(resultId) {
    try {
        const response = await fetch(`${ENDPOINTS.results}/${resultId}`);
        if (!response.ok) throw new Error('Failed to load result details');
        
        const result = await response.json();
        showResultModal(result);
    } catch (error) {
        console.error('Error loading result details:', error);
        showError('Failed to load result details');
    }
}

// Show result modal
function showResultModal(result) {
    const modalBody = document.getElementById('modal-body');
    
    modalBody.innerHTML = `
        <div class="result-details">
            <p><strong>ID:</strong> ${result.id}</p>
            <p><strong>URL:</strong> <a href="${result.url}" target="_blank">${result.url}</a></p>
            <p><strong>Status:</strong> <span class="status-badge status-${result.status}">${result.status}</span></p>
            <p><strong>Response Time:</strong> ${result.response_time || 0}ms</p>
            <p><strong>Timestamp:</strong> ${new Date(result.timestamp).toLocaleString()}</p>
            ${result.error ? `<p><strong>Error:</strong> ${result.error}</p>` : ''}
            ${result.data ? `<p><strong>Data:</strong></p><pre>${JSON.stringify(result.data, null, 2)}</pre>` : ''}
        </div>
    `;
    
    document.getElementById('result-modal').style.display = 'block';
}

// Initialize charts
function initializeCharts() {
    // Time series chart
    const timeCtx = document.getElementById('timeChart').getContext('2d');
    timeChart = new Chart(timeCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Scrapes per Hour',
                data: [],
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    // Status distribution chart
    const statusCtx = document.getElementById('statusChart').getContext('2d');
    statusChart = new Chart(statusCtx, {
        type: 'doughnut',
        data: {
            labels: ['Success', 'Failed', 'Pending'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [
                    '#10b981',
                    '#ef4444',
                    '#f59e0b'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Update charts with new data
function updateCharts(stats) {
    // Update time series chart
    if (stats.hourly_data && timeChart) {
        timeChart.data.labels = stats.hourly_data.labels || [];
        timeChart.data.datasets[0].data = stats.hourly_data.data || [];
        timeChart.update();
    }
    
    // Update status distribution chart
    if (stats.status_distribution && statusChart) {
        statusChart.data.datasets[0].data = [
            stats.status_distribution.success || 0,
            stats.status_distribution.failed || 0,
            stats.status_distribution.pending || 0
        ];
        statusChart.update();
    }
}

// Update timestamp
function updateTimestamp() {
    const timestamp = new Date().toLocaleString();
    document.querySelector('.timestamp').textContent = timestamp;
}

// Show error message
function showError(message) {
    // You could implement a toast notification here
    console.error(message);
}

// Export functions for use in HTML onclick handlers
window.viewDetails = viewDetails;