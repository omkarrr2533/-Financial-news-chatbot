// Chart management
let impactChart = null;

function createImpactChart(data) {
    const ctx = document.getElementById('impactChart');
    
    if (!ctx) return;
    
    // Destroy existing chart
    if (impactChart) {
        impactChart.destroy();
    }
    
    // Prepare data
    const institutions = Object.keys(data).slice(0, 10);
    const scores = institutions.map(inst => data[inst].impact_score);
    const colors = institutions.map(inst => {
        const sentiment = data[inst].sentiment;
        if (sentiment === 'Positive') return 'rgba(16, 185, 129, 0.8)';
        if (sentiment === 'Negative') return 'rgba(239, 68, 68, 0.8)';
        return 'rgba(251, 191, 36, 0.8)';
    });
    
    // Create chart
    impactChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: institutions,
            datasets: [{
                label: 'Impact Score',
                data: scores,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.8', '1')),
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.9)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#cbd5e1',
                    borderColor: '#475569',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            const inst = institutions[context.dataIndex];
                            const instData = data[inst];
                            return [
                                `Impact Score: ${context.parsed.y.toFixed(2)}`,
                                `Sentiment: ${instData.sentiment}`,
                                `Mentions: ${instData.mentions}`,
                                `India Linkage: ${instData.india_linkage}`
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(71, 85, 105, 0.3)'
                    },
                    ticks: {
                        color: '#cbd5e1'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#cbd5e1',
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
}

function updateChart(data) {
    if (impactChart && data) {
        const institutions = Object.keys(data).slice(0, 10);
        const scores = institutions.map(inst => data[inst].impact_score);
        const colors = institutions.map(inst => {
            const sentiment = data[inst].sentiment;
            if (sentiment === 'Positive') return 'rgba(16, 185, 129, 0.8)';
            if (sentiment === 'Negative') return 'rgba(239, 68, 68, 0.8)';
            return 'rgba(251, 191, 36, 0.8)';
        });
        
        impactChart.data.labels = institutions;
        impactChart.data.datasets[0].data = scores;
        impactChart.data.datasets[0].backgroundColor = colors;
        impactChart.data.datasets[0].borderColor = colors.map(c => c.replace('0.8', '1'));
        
        impactChart.update('active');
    }
}

// Create sentiment distribution pie chart
function createSentimentChart(containerId, data) {
    const ctx = document.getElementById(containerId);
    
    if (!ctx) return null;
    
    let positiveCount = 0;
    let negativeCount = 0;
    let mixedCount = 0;
    
    Object.values(data).forEach(inst => {
        if (inst.sentiment === 'Positive') positiveCount++;
        else if (inst.sentiment === 'Negative') negativeCount++;
        else mixedCount++;
    });
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Negative', 'Mixed'],
            datasets: [{
                data: [positiveCount, negativeCount, mixedCount],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(251, 191, 36, 0.8)'
                ],
                borderColor: [
                    'rgba(16, 185, 129, 1)',
                    'rgba(239, 68, 68, 1)',
                    'rgba(251, 191, 36, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#cbd5e1',
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.9)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#cbd5e1',
                    borderColor: '#475569',
                    borderWidth: 1,
                    padding: 12
                }
            }
        }
    });
}

// Create trend line chart
function createTrendChart(containerId, historicalData) {
    const ctx = document.getElementById(containerId);
    
    if (!ctx) return null;
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: historicalData.labels,
            datasets: [{
                label: 'Average Impact Score',
                data: historicalData.values,
                borderColor: 'rgba(59, 130, 246, 1)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointBackgroundColor: 'rgba(59, 130, 246, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#cbd5e1',
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.9)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#cbd5e1',
                    borderColor: '#475569',
                    borderWidth: 1,
                    padding: 12
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(71, 85, 105, 0.3)'
                    },
                    ticks: {
                        color: '#cbd5e1'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(71, 85, 105, 0.3)'
                    },
                    ticks: {
                        color: '#cbd5e1'
                    }
                }
            }
        }
    });
}

// Export functions for use in other scripts
window.chartFunctions = {
    createImpactChart,
    updateChart,
    createSentimentChart,
    createTrendChart
};