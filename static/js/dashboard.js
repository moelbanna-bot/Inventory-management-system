// Chart.js global defaults
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.plugins.legend.position = "top";
Chart.defaults.plugins.legend.labels.padding = 20;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.pointStyle = "circle";

// Common chart options
const commonOptions = {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 2,
    plugins: {
        legend: {
            display: true,
            labels: {
                padding: 15,
                usePointStyle: true,
                pointStyle: "circle",
                font: {
                    size: 11,
                },
            },
        },
        tooltip: {
            backgroundColor: "rgba(0, 0, 0, 0.8)",
            padding: 10,
            titleFont: {size: 12},
            bodyFont: {size: 11},
        },
    },
    animation: {
        duration: 2000,
        easing: "easeInOutQuart",
    },
};

// Initialize dashboard charts
function initializeDashboardCharts(chartData) {
    // Inventory Trends Chart
    new Chart(document.getElementById("inventoryTrendsChart").getContext("2d"), {
        type: "line",
        data: {
            labels: chartData.inventory_trends_labels,
            datasets: [
                {
                    label: "Total Inventory",
                    data: chartData.inventory_trends_data,
                    borderColor: "#3498db",
                    backgroundColor: "rgba(52, 152, 219, 0.1)",
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: "#3498db",
                    pointBorderColor: "#fff",
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                },
            ],
        },
        options: {
            ...commonOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {color: "rgba(0, 0, 0, 0.05)"},
                    ticks: {font: {size: 12}},
                },
                x: {
                    grid: {display: false},
                    ticks: {font: {size: 12}},
                },
            },
        },
    });

    // Shipment Status Chart
    new Chart(document.getElementById("shipmentStatusChart").getContext("2d"), {
        type: "doughnut",
        data: {
            labels: chartData.shipment_status_labels,
            datasets: [
                {
                    data: chartData.shipment_status_data,
                    backgroundColor: ["#2ecc71", "#f1c40f", "#e74c3c", "#3498db"],
                    borderWidth: 0,
                    borderRadius: 5,
                },
            ],
        },
        options: {
            ...commonOptions,
            plugins: {
                ...commonOptions.plugins,
                legend: {
                    ...commonOptions.plugins.legend,
                    position: "right",
                },
            },
            cutout: "70%",
            animation: {
                ...commonOptions.animation,
                animateScale: true,
                animateRotate: true,
            },
        },
    });

    // Monthly Shipments Chart
    new Chart(document.getElementById("monthlyShipmentsChart").getContext("2d"), {
        type: "bar",
        data: {
            labels: chartData.monthly_shipments_labels,
            datasets: [
                {
                    label: "Shipments",
                    data: chartData.monthly_shipments_data,
                    backgroundColor: "#3498db",
                    borderRadius: 5,
                },
            ],
        },
        options: {
            ...commonOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {color: "rgba(0, 0, 0, 0.05)"},
                    ticks: {font: {size: 12}},
                },
                x: {
                    grid: {display: false},
                    ticks: {font: {size: 12}},
                },
            },
        },
    });

    // Top Products Chart
    new Chart(document.getElementById("topProductsChart").getContext("2d"), {
        type: "bar",
        data: {
            labels: chartData.top_products_labels,
            datasets: [
                {
                    label: "Quantity",
                    data: chartData.top_products_data,
                    backgroundColor: "#2ecc71",
                    borderRadius: 5,
                },
            ],
        },
        options: {
            ...commonOptions,
            indexAxis: "y",
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {color: "rgba(0, 0, 0, 0.05)"},
                    ticks: {font: {size: 12}},
                },
                y: {
                    grid: {display: false},
                    ticks: {font: {size: 12}},
                },
            },
        },
    });
}
