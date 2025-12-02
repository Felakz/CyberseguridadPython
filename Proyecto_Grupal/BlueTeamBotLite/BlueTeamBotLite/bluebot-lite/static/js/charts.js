// BlueTeamBot Charts Utilities

/**
 * Colores consistentes para los gráficos
 */
const CHART_COLORS = {
    HIGH: {
        border: 'rgb(220, 53, 69)',
        background: 'rgba(220, 53, 69, 0.1)'
    },
    MEDIUM: {
        border: 'rgb(255, 193, 7)',
        background: 'rgba(255, 193, 7, 0.1)'
    },
    LOW: {
        border: 'rgb(25, 135, 84)',
        background: 'rgba(25, 135, 84, 0.1)'
    }
};

/**
 * Configuración por defecto para gráficos de línea
 */
const DEFAULT_LINE_OPTIONS = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
        legend: {
            position: 'top'
        },
        tooltip: {
            mode: 'index',
            intersect: false
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            ticks: {
                precision: 0
            }
        }
    },
    interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
    }
};

/**
 * Configuración por defecto para gráficos de pastel
 */
const DEFAULT_PIE_OPTIONS = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
        legend: {
            position: 'bottom'
        },
        tooltip: {
            callbacks: {
                label: function(context) {
                    let label = context.label || '';
                    if (label) {
                        label += ': ';
                    }
                    label += context.parsed;
                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                    const percentage = ((context.parsed / total) * 100).toFixed(1);
                    label += ` (${percentage}%)`;
                    return label;
                }
            }
        }
    }
};

/**
 * Crea un gráfico de línea de tendencias
 */
function createTrendChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [
                {
                    label: 'HIGH',
                    data: data.HIGH,
                    borderColor: CHART_COLORS.HIGH.border,
                    backgroundColor: CHART_COLORS.HIGH.background,
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'MEDIUM',
                    data: data.MEDIUM,
                    borderColor: CHART_COLORS.MEDIUM.border,
                    backgroundColor: CHART_COLORS.MEDIUM.background,
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'LOW',
                    data: data.LOW,
                    borderColor: CHART_COLORS.LOW.border,
                    backgroundColor: CHART_COLORS.LOW.background,
                    tension: 0.3,
                    fill: true
                }
            ]
        },
        options: DEFAULT_LINE_OPTIONS
    });
}

/**
 * Crea un gráfico de pastel
 */
function createPieChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['HIGH', 'MEDIUM', 'LOW'],
            datasets: [{
                data: [data.HIGH, data.MEDIUM, data.LOW],
                backgroundColor: [
                    CHART_COLORS.HIGH.border,
                    CHART_COLORS.MEDIUM.border,
                    CHART_COLORS.LOW.border
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: DEFAULT_PIE_OPTIONS
    });
}

/**
 * Formatea un número con separadores de miles
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Formatea una fecha de ISO a formato legible
 */
function formatDate(isoDate) {
    const date = new Date(isoDate);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Muestra un mensaje de error
 */
function showError(message) {
    console.error(message);
    alert('Error: ' + message);
}

/**
 * Obtiene el color según la severidad
 */
function getSeverityColor(severity) {
    switch(severity) {
        case 'HIGH': return 'danger';
        case 'MEDIUM': return 'warning';
        case 'LOW': return 'success';
        default: return 'secondary';
    }
}

/**
 * Obtiene el icono según la severidad
 */
function getSeverityIcon(severity) {
    switch(severity) {
        case 'HIGH': return 'exclamation-octagon';
        case 'MEDIUM': return 'exclamation-triangle';
        case 'LOW': return 'info-circle';
        default: return 'question-circle';
    }
}
