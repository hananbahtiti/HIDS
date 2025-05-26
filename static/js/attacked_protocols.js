function handleExport() {
  const format = document.getElementById('allExportType').value;
  const table = document.getElementById('protocolTable');
  const rows = Array.from(table.querySelectorAll('tr'));
  
  const csv = rows.map(row =>
    Array.from(row.querySelectorAll('th, td'))
      .map(cell => `"${cell.innerText}"`)
      .join(',')
  ).join('\n');

  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = format === 'excel' ? 'protocols.xlsx' : 'protocols.csv';

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}