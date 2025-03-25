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
  aspectRatio: window.innerWidth < 768 ? 1 : 2,
  plugins: {
    legend: {
      display: true,
      labels: {
        padding: 15,
        usePointStyle: true,
        pointStyle: "circle",
        font: {
          size: window.innerWidth < 768 ? 9 : 11,
        },
      },
      position: window.innerWidth < 768 ? "bottom" : "top",
    },
    tooltip: {
      backgroundColor: "rgba(0, 0, 0, 0.8)",
      padding: 10,
      titleFont: { size: window.innerWidth < 768 ? 10 : 12 },
      bodyFont: { size: window.innerWidth < 768 ? 9 : 11 },
    },
  },
  animation: {
    duration: 2000,
    easing: "easeInOutQuart",
  },
};

// Get shared mobile options
function getMobileOptions() {
  const isMobile = window.innerWidth < 768;
  return {
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: "rgba(0, 0, 0, 0.05)" },
        ticks: {
          font: { size: isMobile ? 9 : 12 },
          maxTicksLimit: isMobile ? 5 : 10,
        },
      },
      x: {
        grid: { display: false },
        ticks: {
          font: { size: isMobile ? 9 : 12 },
          maxTicksLimit: isMobile ? 5 : 10,
        },
      },
    },
  };
}

// Initialize Inventory Trends Chart
function initializeInventoryTrendsChart(chartData) {
  const isMobile = window.innerWidth < 768;
  const ctx = document.getElementById("inventoryTrendsChart");
  if (!ctx) return null;

  return new Chart(ctx.getContext("2d"), {
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
          pointRadius: isMobile ? 2 : 4,
          pointHoverRadius: isMobile ? 3 : 6,
        },
      ],
    },
    options: {
      ...commonOptions,
      ...getMobileOptions(),
    },
  });
}

// Initialize Shipment Status Chart
function initializeShipmentStatusChart(chartData) {
  const isMobile = window.innerWidth < 768;
  const ctx = document.getElementById("shipmentStatusChart");
  if (!ctx) return null;

  return new Chart(ctx.getContext("2d"), {
    type: "pie",
    data: {
      labels: chartData.shipment_status_labels,
      datasets: [
        {
          data: chartData.shipment_status_data,
          backgroundColor: [
            "#2ecc71",
            "#f1c40f",
            "#e74c3c",
            "#3498db",
            "#9b59b6",
          ],
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
          position: isMobile ? "bottom" : "right",
          labels: {
            padding: isMobile ? 10 : 15,
            usePointStyle: true,
            pointStyle: "circle",
            boxWidth: isMobile ? 8 : 10,
            font: {
              size: isMobile ? 9 : 11,
            },
          },
        },
      },
      animation: {
        ...commonOptions.animation,
        animateScale: true,
        animateRotate: true,
      },
    },
  });
}

// Initialize Monthly Shipments Chart
function initializeMonthlyShipmentsChart(chartData) {
  const ctx = document.getElementById("monthlyShipmentsChart");
  if (!ctx) return null;

  return new Chart(ctx.getContext("2d"), {
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
      ...getMobileOptions(),
      responsive: true,
      maintainAspectRatio: false,
    },
  });
}

// Initialize Top Products Chart
function initializeTopProductsChart(chartData) {
  const isMobile = window.innerWidth < 768;
  const ctx = document.getElementById("topProductsChart");
  if (!ctx) return null;

  return new Chart(ctx.getContext("2d"), {
    type: "bar",
    data: {
      labels: isMobile
        ? chartData.top_products_labels.slice(0, 5)
        : chartData.top_products_labels,
      datasets: [
        {
          label: "Quantity",
          data: isMobile
            ? chartData.top_products_data.slice(0, 5)
            : chartData.top_products_data,
          backgroundColor: "#2ecc71",
          borderRadius: 5,
        },
      ],
    },
    options: {
      ...commonOptions,
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          beginAtZero: true,
          grid: { color: "rgba(0, 0, 0, 0.05)" },
          ticks: {
            font: { size: isMobile ? 9 : 12 },
            maxTicksLimit: isMobile ? 5 : 10,
          },
        },
        y: {
          grid: { display: false },
          ticks: {
            font: { size: isMobile ? 9 : 12 },
            callback: function (value) {
              // Truncate long product names on mobile
              if (isMobile && this.getLabelForValue(value).length > 15) {
                return this.getLabelForValue(value).substring(0, 12) + "...";
              }
              return this.getLabelForValue(value);
            },
          },
        },
      },
    },
  });
}

// Legacy function for backward compatibility
function initializeDashboardCharts(chartData) {
  const charts = {};
  charts.inventoryTrendsChart = initializeInventoryTrendsChart(chartData);
  charts.shipmentStatusChart = initializeShipmentStatusChart(chartData);
  charts.monthlyShipmentsChart = initializeMonthlyShipmentsChart(chartData);
  charts.topProductsChart = initializeTopProductsChart(chartData);
  return charts;
}
