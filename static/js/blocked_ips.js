function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function handleBlockManually() {
    const ipInput = document.getElementById('ipInput');
    const attackInput = document.getElementById('attackTypeInput');
    const ip = ipInput.value.trim();
    const attackType = attackInput.value.trim();

    if (!ip || !attackType) {
        alert('Please fill in both IP Address and Attack Type');
        return;
    }

    fetch('/api/add_blocked_ip/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ ip: ip, attack_type: attackType }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert(data.message);
            updateBlockedTable(data.blocked_ips);
            ipInput.value = '';
            attackInput.value = '';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error blocking IP');
    });
}


function updateBlockedTable(blockedIps) {
    const tbody = document.getElementById('blockedTableBody');
    tbody.innerHTML = ''; // امسح الجدول القديم

    blockedIps.forEach(ipData => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${ipData.ip_address}</td>
            <td>${ipData.attack_type}</td>
            <td class="status-alert">Blocked</td>
            <td><button class="btn-unblock" onclick="handleUnblockIP('${ipData.ip_address}')">Unblock</button></td>
        `;
        tbody.appendChild(row);
    });
}


function loadBlockedIPsOnPageLoad() {
    fetch('/api/get_blocked_ips/')
        .then(response => response.json())
        .then(data => {
            updateBlockedTable(data.blocked_ips);
        });
}
window.onload = loadBlockedIPsOnPageLoad;






function addBlockedIPToTable(ip, attackType) {
    const tbody = document.getElementById('blockedTableBody');
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${ip}</td>
        <td>${attackType}</td>
        <td class="status-alert">Blocked</td>
        <td><button class="btn-unblock" onclick="handleUnblockIP('${ip}')">Unblock</button></td>
    `;
    tbody.appendChild(row);
}
    





  
function exportAllIPs() {
    const format = document.getElementById("allExportFormat").value;
    const table = document.getElementById("allTableBody");
    let data = [["Block", "IP Address", "Status"]];
  
    for (let row of table.rows) {
      let rowData = [];
      for (let i = 0; i < 3; i++) {
        rowData.push(row.cells[i].innerText.trim());
      }
      data.push(rowData);
    }
  
    if (format === "csv") {
      exportToCSVWithData(data, "all_ips.csv");
    } else if (format === "excel") {
      exportToExcelWithData(data, "all_ips.xls");
    }
  }
  
  function exportToCSVWithData(data, filename) {
    let csvContent = data.map(e => e.join(",")).join("\n");
    let blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    let url = URL.createObjectURL(blob);
    let link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
  
  function exportToExcelWithData(data, filename) {
    let table = '<table><tr>';
    data[0].forEach(header => {
      table += `<th>${header}</th>`;
    });
    table += '</tr>';
  
    for (let i = 1; i < data.length; i++) {
      table += '<tr>';
      data[i].forEach(cell => {
        table += `<td>${cell}</td>`;
      });
      table += '</tr>';
    }
  
    table += '</table>';
    const blob = new Blob([table], { type: "application/vnd.ms-excel" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }



  function exportData() {
    const format = document.getElementById("exportFormat").value;
    const table = document.getElementById("blockedTableBody");
    let data = [["IP Address", "Attack Type", "Status"]];
  
    for (let row of table.rows) {
      let rowData = [];
      for (let i = 0; i < 3; i++) {  // نأخذ فقط الأعمدة الثلاثة الأولى (بدون الزر)
        rowData.push(row.cells[i].innerText.trim());
      }
      data.push(rowData);
    }
  
    if (format === "csv") {
      exportToCSV(data);
    } else if (format === "excel") {
      exportToExcel(data);
    }
  }
  
  function exportToCSV(data) {
    let csvContent = data.map(e => e.join(",")).join("\n");
    let blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    let url = URL.createObjectURL(blob);
    let link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "blocked_ips.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
  
  function exportToExcel(data) {
    let table = '<table><tr>';
    data[0].forEach(header => {
      table += `<th>${header}</th>`;
    });
    table += '</tr>';
  
    for (let i = 1; i < data.length; i++) {
      table += '<tr>';
      data[i].forEach(cell => {
        table += `<td>${cell}</td>`;
      });
      table += '</tr>';
    }
  
    table += '</table>';
    const blob = new Blob([table], { type: "application/vnd.ms-excel" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "blocked_ips.xls");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }



  function handleUnblockIP(ip) {
    if (!confirm(`Are you sure you want to unblock ${ip}?`)) return;

    fetch('/api/unblock_ip/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),  // تأكد أن لديك هذه الدالة أو استخدم @csrf_exempt
        },
        body: JSON.stringify({ ip: ip })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            // إزالة الـ IP من جدول المحظورين
            const row = document.querySelector(`#blockedTableBody tr td:first-child:contains('${ip}')`);
            if (row) {
                const rowElement = row.closest("tr");
                rowElement.remove();

                // إضافته إلى جدول All Network IPs
                const newRow = document.createElement('tr');
                newRow.innerHTML = `
                    <td><button class="btn-block">Block</button></td>
                    <td>${ip}</td>
                    <td class="status-active">Normal</td>
                `;
                document.getElementById("allTableBody").appendChild(newRow);
            }
        } else {
            alert(data.error || "Error unblocking IP.");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("An error occurred while unblocking.");
    });
}

// دالة لجلب CSRF من الكوكيز
function getCSRFToken() {
    let csrfToken = null;
    const cookies = document.cookie.split(';');
    cookies.forEach(cookie => {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            csrfToken = value;
        }
    });
    return csrfToken;
}



function handleUnblockIP(ip) {
  fetch('/api/unblock_ip/', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify({ ip: ip })
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
          refreshBlockedIPs();    // إعادة تحميل جدول المحظورين
          refreshAllIPs();        // إعادة تحميل جدول الشبكة الكاملة
      } else {
          alert(data.error || "Failed to unblock IP.");
      }
  })
  .catch(error => {
      console.error("Unblock error:", error);
  });
}

function refreshBlockedIPs() {
  fetch('/api/get_blocked_ips/')
      .then(response => response.json())
      .then(data => {
          const tbody = document.getElementById('blockedTableBody');
          tbody.innerHTML = '';

          if (data.blocked_ips.length > 0) {
              data.blocked_ips.forEach(ip => {
                  const row = document.createElement('tr');
                  row.innerHTML = `
                      <td>${ip.ip_address}</td>
                      <td>${ip.attack_type}</td>
                      <td class="${ip.status === 'Blocked' ? 'status-alert' : 'status-detected'}">${ip.status}</td>
                      <td>
                          ${ip.status === 'Blocked'
                              ? `<button class="btn-unblock" onclick="handleUnblockIP('${ip.ip_address}')">Unblock</button>`
                              : '<span style="color: gray;">N/A</span>'}
                      </td>
                  `;
                  tbody.appendChild(row);
              });
          } else {
              tbody.innerHTML = '<tr><td colspan="4">No blocked IPs found.</td></tr>';
          }
      })
      .catch(error => console.error("Error fetching blocked IPs:", error));
}

function refreshAllIPs() {
  fetch('/api/get_all_ips/')
      .then(response => response.json())
      .then(data => {
          const tbody = document.getElementById('allTableBody');
          tbody.innerHTML = '';

          if (data.normal_ips.length > 0) {
              data.normal_ips.forEach(ip => {
                  const row = document.createElement('tr');
                  row.innerHTML = `
                      <td><button class="btn-block" onclick="handleBlock('${ip}')">Block</button></td>
                      <td>${ip}</td>
                      <td class="status-active">Normal</td>
                  `;
                  tbody.appendChild(row);
              });
          } else {
              tbody.innerHTML = '<tr><td colspan="3">No normal IPs found.</td></tr>';
          }
      })
      .catch(error => console.error("Error fetching all IPs:", error));
}

// دالة لجلب CSRF Token من الكوكيز
function getCSRFToken() {
  let cookieValue = null;
  const name = 'csrftoken';
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
          cookie = cookie.trim();
          if (cookie.startsWith(name + '=')) {
              cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}
