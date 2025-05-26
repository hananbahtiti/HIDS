const attackChartCtx = document.getElementById('attackChart').getContext('2d');
const protocolChartCtx = document.getElementById('protocolChart').getContext('2d');
const severityChartCtx = document.getElementById('severityChart').getContext('2d');

const attackChart = new Chart(attackChartCtx, {
  type: 'line',
  data: {
    labels: ['January', 'February', 'March', 'April', 'May', 'June'],
    datasets: [{
      label: 'Number of Attacks Over Time',
      data: [10, 20, 30, 40, 50, 60],
      borderColor: '#d2691e',
      fill: false
    }]
  }
});

const protocolChart = new Chart(protocolChartCtx, {
  type: 'pie',
  data: {
    labels: ['TCP', 'UDP', 'ICMP'],
    datasets: [{
      label: 'Protocols',
      data: [40, 30, 30],
      backgroundColor: ['#ff6347', '#4682b4', '#32cd32']
    }]
  }
});

const severityChart = new Chart(severityChartCtx, {
  type: 'bar',
  data: {
    labels: ['Low', 'Medium', 'High'],
    datasets: [{
      label: 'Average Attack Severity',
      data: [5, 10, 15],
      backgroundColor: ['#7bc96f', '#f1c232', '#e6733c']
    }]
  }
});
