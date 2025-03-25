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
      titleFont: { size: 12 },
      bodyFont: { size: 11 },
    },
  },
  animation: {
    duration: 2000,
    easing: "easeInOutQuart",
  },
};

// Variables to store chart instances
let ordersStatusChart;
let shipmentStatusChart;
let monthlyShipmentsChart;
let topProductsChart;

// Initialize dashboard charts
function initializeDashboardCharts(chartData) {
  // Orders Status Distribution Chart (replacing Inventory Trends)
  ordersStatusChart = new Chart(
    document.getElementById("ordersStatusChart").getContext("2d"),
    {
      type: "pie",
      data: {
        labels: chartData.orders_status_labels,
        datasets: [
          {
            data: chartData.orders_status_data,
            backgroundColor: [
              "#2ecc71", // Completed/Delivered
              "#f1c40f", // Processing
              "#e74c3c", // Canceled
              "#3498db", // Pending
              "#9b59b6", // Other statuses
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
            position: "right",
          },
        },
        animation: {
          ...commonOptions.animation,
          animateScale: true,
          animateRotate: true,
        },
      },
    }
  );

  // Shipment Status Chart
  shipmentStatusChart = new Chart(
    document.getElementById("shipmentStatusChart").getContext("2d"),
    {
      type: "pie",
      data: {
        labels: chartData.shipment_status_labels,
        datasets: [
          {
            data: chartData.shipment_status_data,
            backgroundColor: [
              "#e74c3c",
              "#3498db",
              "#2ecc71",
              "#f1c40f",
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
            position: "right",
          },
        },
        animation: {
          ...commonOptions.animation,
          animateScale: true,
          animateRotate: true,
        },
      },
    }
  );

  // Initialize tab event listeners
  initializeTabEvents(chartData);
}

// Initialize reporting tab charts
function initializeReportingCharts(chartData) {
  // Monthly Shipments Chart
  if (!monthlyShipmentsChart) {
    monthlyShipmentsChart = new Chart(
      document.getElementById("monthlyShipmentsChart").getContext("2d"),
      {
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
              grid: { color: "rgba(0, 0, 0, 0.05)" },
              ticks: { font: { size: 12 } },
            },
            x: {
              grid: { display: false },
              ticks: { font: { size: 12 } },
            },
          },
        },
      }
    );
  }

  // Top Products Chart
  if (!topProductsChart) {
    topProductsChart = new Chart(
      document.getElementById("topProductsChart").getContext("2d"),
      {
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
              grid: { color: "rgba(0, 0, 0, 0.05)" },
              ticks: { font: { size: 12 } },
            },
            y: {
              grid: { display: false },
              ticks: { font: { size: 12 } },
            },
          },
        },
      }
    );
  }
}

// Initialize tab events
function initializeTabEvents(chartData) {
  // Get all tab links
  const tabLinks = document.querySelectorAll(".nav-link");

  // Add click event listeners to each tab
  tabLinks.forEach((tab) => {
    tab.addEventListener("click", function (e) {
      // Check if this is the reporting tab
      if (e.target.getAttribute("href") === "#reporting") {
        // Wait a short time for the tab to become visible
        setTimeout(() => {
          initializeReportingCharts(chartData);
        }, 100);
      }
    });
  });

  // Check if URL hash points to reporting tab
  if (window.location.hash === "#reporting") {
    // Initialize reporting charts as the tab is already active
    setTimeout(() => {
      initializeReportingCharts(chartData);
    }, 100);
  }
}
