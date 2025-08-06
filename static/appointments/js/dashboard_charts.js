function renderBarChart(canvasId, data, label, labelField, valueField, color = 'blue') {
    const ctx = document.getElementById(canvasId);

    if (!ctx || !Array.isArray(data) || data.length === 0) {
        console.warn(`⚠️ Dados inválidos para ${canvasId}:`, data);
        return;
    }

    const labels = data.map(item => item[labelField] || 'Unknown');
    const values = data.map(item => item[valueField] || 0);

    // Paleta de cores por status (caso gráfico de status)
    const statusColors = {
        "on time": "#4CAF50",      // verde
        "rescheduled": "#FFEB3B",  // amarelo
        "canceled": "#FF9800",     // laranja
        "no show up": "#F44336",   // vermelho
    };
    const backgroundColors = labels.map(label => {
        const normalized = label.trim().toLowerCase();  // remove espaços e põe em minúsculas
        return statusColors[normalized] || color;
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                backgroundColor: backgroundColors,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: "#6B778C"
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: "#6B778C" },
                    grid: { color: "#E0E0E0" }
                },
                x: {
                    ticks: { color: "#6B778C" },
                    grid: { display: false }
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    // Gráficos Pallets por Checker
    renderBarChart("checkerChartDay", checkerDayData, "Pallets per Checker - Today", "checker__name", "total", "#42A5F5");
    renderBarChart("checkerChartWeek", checkerWeekData, "Pallets per Checker - This Week", "checker__name", "total", "#FFCA28");
    renderBarChart("checkerChartMonth", checkerMonthData, "Pallets per Checker - This Month", "checker__name", "total", "#26C6DA");

    // Gráficos Loads por Status com cores distintas por status
    renderBarChart("statusChartDay", statusDayData, "Loads by Status - Today", "status_load", "count", "#999999");
    renderBarChart("statusChartWeek", statusWeekData, "Loads by Status - This Week", "status_load", "count", "#999999");
    renderBarChart("statusChartMonth", statusMonthData, "Loads by Status - This Month", "status_load", "count", "#999999");
});
