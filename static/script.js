document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('stockSearch');
    const searchResults = document.getElementById('searchResults');
    const stockTitle = document.getElementById('stockTitle');
    const stockSector = document.getElementById('stockSector');
    const stockCount = document.getElementById('stockCount');
    const noData = document.getElementById('noData');
    const loading = document.getElementById('loading');
    const tableBody = document.querySelector('#dataTable tbody');

    // News Elements
    const newsSection = document.getElementById('newsSection');
    const newsGrid = document.getElementById('newsGrid');
    const impactContainer = document.getElementById('impactContainer');
    const impactMessage = document.getElementById('impactMessage');
    const marketNewsGrid = document.getElementById('marketNewsGrid');
    const refreshMarketNews = document.getElementById('refreshMarketNews');

    let stocks = [];
    let chartInstance = null;

    // Fetch stock list on load
    fetch('/api/stocks')
        .then(response => response.json())
        .then(data => {
            stocks = data;
        })
        .catch(err => console.error('Error fetching stock list:', err));

    // Initial Market News load
    fetchMarketNews();

    if (refreshMarketNews) {
        refreshMarketNews.addEventListener('click', fetchMarketNews);
    }

    // Search functionality
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();

        if (query.length < 2) {
            searchResults.classList.add('hidden');
            return;
        }

        const filtered = stocks.filter(stock =>
            stock.ticker.toLowerCase().includes(query) ||
            stock.name.toLowerCase().includes(query)
        ).slice(0, 10); // Limit to 10 results

        renderSearchResults(filtered);
    });

    function renderSearchResults(results) {
        searchResults.innerHTML = '';
        if (results.length === 0) {
            searchResults.classList.add('hidden');
            return;
        }

        results.forEach(stock => {
            const div = document.createElement('div');
            div.className = 'search-item';
            div.innerHTML = `
                <span class="search-ticker">${stock.ticker}</span>
                <span class="search-name">${stock.name}</span>
            `;
            div.addEventListener('click', () => {
                selectStock(stock);
                searchResults.classList.add('hidden');
                searchInput.value = ''; // Clear input
            });
            searchResults.appendChild(div);
        });

        searchResults.classList.remove('hidden');
    }

    // Hide search results if clicked outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.add('hidden');
        }
    });

    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    const applyFilterBtn = document.getElementById('applyFilter');

    // Current selected stock
    let currentStock = null;

    function selectStock(stock) {
        currentStock = stock; // Store current stock
        stockTitle.textContent = `${stock.name} (${stock.ticker})`;
        stockSector.textContent = stock.sector || 'N/A';

        fetchStockData(stock.ticker);
        fetchStockNews(stock.ticker);
    }

    applyFilterBtn.addEventListener('click', () => {
        if (currentStock) {
            fetchStockData(currentStock.ticker);
        }
    });

    function fetchStockData(ticker) {
        // Show loading
        loading.classList.remove('hidden');
        noData.classList.add('hidden');
        if (chartInstance) {
            chartInstance.destroy(); // Clear old chart
            chartInstance = null;
        }
        tableBody.innerHTML = '';

        let url = `/api/data/${ticker}`;

        const params = new URLSearchParams();
        if (startDateInput.value) params.append('start', startDateInput.value);
        if (endDateInput.value) params.append('end', endDateInput.value);

        if (params.toString()) {
            url += `?${params.toString()}`;
        }

        fetch(url)
            .then(res => res.json())
            .then(data => {
                loading.classList.add('hidden');
                if (data.error || data.data.length === 0) {
                    noData.textContent = "No data available for selected range";
                    noData.classList.remove('hidden');
                    stockCount.textContent = '0';
                    return;
                }

                stockCount.textContent = data.count.toLocaleString();
                renderChart(data);
                renderTable(data.data);
            })
            .catch(err => {
                loading.classList.add('hidden');
                console.error(err);
                noData.textContent = "Error fetching data";
                noData.classList.remove('hidden');
            });
    }

    function renderChart(apiData) {
        const ctx = document.getElementById('priceChart').getContext('2d');
        const labels = apiData.data.map(d => d.date);
        const prices = apiData.data.map(d => d.close);

        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(0, 242, 234, 0.5)'); // Accent color
        gradient.addColorStop(1, 'rgba(0, 242, 234, 0.0)');

        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Close Price (INR)',
                    data: prices,
                    borderColor: '#00f2ea',
                    backgroundColor: gradient,
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    y: {
                        display: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    }
                }
            }
        });
    }

    function renderTable(data) {
        // Reverse for table (newest first)
        const reversedData = [...data].reverse();
        const rows = reversedData.slice(0, 50).map(row => `
            <tr>
                <td>${row.date}</td>
                <td>${row.open ? row.open.toFixed(2) : '-'}</td>
                <td>${row.high ? row.high.toFixed(2) : '-'}</td>
                <td>${row.low ? row.low.toFixed(2) : '-'}</td>
                <td>${row.close ? row.close.toFixed(2) : '-'}</td>
                <td>${row.volume ? row.volume.toLocaleString() : '-'}</td>
            </tr>
        `).join('');

        tableBody.innerHTML = rows;
    }

    // --- SQL Playground Logic ---
    const sqlQuery = document.getElementById('sqlQuery');
    const runQueryBtn = document.getElementById('runQuery');
    const clearQueryBtn = document.getElementById('clearQuery');
    const sqlError = document.getElementById('sqlError');
    const sqlResultsContainer = document.getElementById('sqlResultsContainer');
    const sqlHeadRow = document.getElementById('sqlHeadRow');
    const sqlBody = document.getElementById('sqlBody');

    if (runQueryBtn) {
        runQueryBtn.addEventListener('click', runSqlQuery);
    }

    if (clearQueryBtn) {
        clearQueryBtn.addEventListener('click', () => {
            sqlQuery.value = '';
            sqlError.classList.add('hidden');
            sqlResultsContainer.classList.add('hidden');
        });
    }

    function runSqlQuery() {
        const query = sqlQuery.value.trim();
        if (!query) return;

        // Reset UI
        sqlError.classList.add('hidden');
        sqlResultsContainer.classList.add('hidden');
        runQueryBtn.textContent = 'Running...';
        runQueryBtn.disabled = true;

        fetch('/api/execute_sql', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        })
            .then(res => res.json())
            .then(data => {
                runQueryBtn.textContent = 'Run Query';
                runQueryBtn.disabled = false;

                if (data.error) {
                    sqlError.textContent = `Error: ${data.error}`;
                    sqlError.classList.remove('hidden');
                    return;
                }

                if (data.message) {
                    sqlError.textContent = data.message;
                    sqlError.style.color = '#00f2ea';
                    sqlError.style.borderColor = 'rgba(0, 242, 234, 0.2)';
                    sqlError.style.backgroundColor = 'rgba(0, 242, 234, 0.1)';
                    sqlError.classList.remove('hidden');
                } else if (data.columns && data.data) {
                    renderSqlTable(data.columns, data.data);
                }
            })
            .catch(err => {
                console.error(err);
                runQueryBtn.textContent = 'Run Query';
                runQueryBtn.disabled = false;
                sqlError.textContent = 'Failed to execute query. Check console for details.';
                sqlError.classList.remove('hidden');
            });
    }

    function renderSqlTable(columns, rows) {
        sqlHeadRow.innerHTML = columns.map(col => `<th>${col}</th>`).join('');

        if (rows.length === 0) {
            sqlBody.innerHTML = '<tr><td colspan="' + columns.length + '" style="text-align:center;">No results found</td></tr>';
        } else {
            sqlBody.innerHTML = rows.map(row => {
                return '<tr>' + row.map(cell => `<td>${cell === null ? 'NULL' : cell}</td>`).join('') + '</tr>';
            }).join('');
        }

        sqlResultsContainer.classList.remove('hidden');
        sqlError.style.color = '';
        sqlError.style.borderColor = '';
        sqlError.style.backgroundColor = '';
    }

    // --- News Logic ---
    function fetchStockNews(ticker) {
        if (!newsSection) return;
        newsSection.classList.add('hidden');
        if (impactContainer) impactContainer.classList.add('hidden');

        fetch(`/api/news/${ticker}`)
            .then(res => res.json())
            .then(data => {
                if (data.news && data.news.length > 0) {
                    renderNewsItems(data.news, newsGrid);
                    newsSection.classList.remove('hidden');
                }

                if (data.impact && data.impact.message && data.impact.data_points > 0 && impactContainer) {
                    impactMessage.textContent = data.impact.message;
                    impactContainer.classList.remove('hidden');
                }
            })
            .catch(err => console.error('Error fetching news:', err));
    }

    function fetchMarketNews() {
        if (!marketNewsGrid) return;
        marketNewsGrid.innerHTML = '<div class="loading">Loading market news...</div>';
        fetch('/api/market_news')
            .then(res => res.json())
            .then(data => {
                renderNewsItems(data, marketNewsGrid, true);
            })
            .catch(err => {
                console.error('Error fetching market news:', err);
                marketNewsGrid.innerHTML = '<div class="no-data">Failed to load news</div>';
            });
    }

    function renderNewsItems(news, container, showTicker = false) {
        if (!container) return;
        container.innerHTML = '';
        if (news.length === 0) {
            container.innerHTML = '<div class="no-data">No news available</div>';
            return;
        }
        news.forEach(item => {
            const sentimentClass = getSentimentClass(item.sentiment);
            const sentimentLabel = getSentimentLabel(item.sentiment);

            const card = document.createElement('div');
            card.className = 'news-card';
            card.innerHTML = `
                <div class="news-header">
                    <span class="news-publisher">${item.publisher}</span>
                    <span class="sentiment-badge ${sentimentClass}">${sentimentLabel}</span>
                </div>
                <a href="${item.url}" target="_blank" class="news-title">${item.headline}</a>
                <p class="news-summary">${item.summary || ''}</p>
                <div class="news-footer">
                    <span>${item.published_at || ''}</span>
                    ${showTicker ? `<span class="ticker-tag">${item.ticker}</span>` : ''}
                </div>
            `;
            container.appendChild(card);
        });
    }

    function getSentimentClass(score) {
        if (score > 0.1) return 'sentiment-positive';
        if (score < -0.1) return 'sentiment-negative';
        return 'sentiment-neutral';
    }

    function getSentimentLabel(score) {
        if (score > 0.1) return 'Positive';
        if (score < -0.1) return 'Negative';
        return 'Neutral';
    }

    // --- Tab Switching Logic ---
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.dataset.tab;

            // Update Nav State
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Update Tab State
            tabContents.forEach(tab => {
                tab.classList.remove('active');
                if (tab.id === `${targetTab}-tab`) {
                    tab.classList.add('active');
                }
            });
        });
    });
});
