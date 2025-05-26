async function updateTable() {
    try {
      // 1. Fetch from FastAPI and store in DB
      const storeResponse = await fetch('/intrusion_results/fetch/');
      const storeData = await storeResponse.json();
  
      if (storeResponse.ok) {
        // 2. Fetch from DB and display
        const viewResponse = await fetch('/intrusion_results/');
        const viewData = await viewResponse.json();
  
        const tableBody = document.querySelector("#resultsTable tbody");
        tableBody.innerHTML = '';
  
        if (viewData.rows) {
          viewData.rows.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
              <td>${row.row_index}</td>
              <td>${row.timestamp}</td>
              <td>${row.ct_src_dport_ltm}</td>
              <td>${row.rate}</td>
              <td>${row.dwin}</td>
              <td>${row.dload}</td>
              <td>${row.swin}</td>
              <td>${row.ct_dst_sport_ltm}</td>
              <td>${row.ct_state_ttl}</td>
              <td>${row.sttl}</td>
              <td>${row.src}</td>
              <td>${row.proto}</td>
              <td>${row.state}</td>
              <td>${row.mse}</td>
              <td>${row.result}</td>
            `;
            tableBody.appendChild(tr);
          });
        } else {
          tableBody.innerHTML = '<tr><td colspan="12">No data available</td></tr>';
        }
      } else {
        alert('Error while fetching from FastAPI');
      }
  
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to update table.');
    }
  }

  

  

  


  function exportData() {
    const format = document.getElementById('exportFormat').value;
    const table = document.getElementById('resultsTable');
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
    link.download = format === 'excel' ? 'results.xlsx' : 'results.csv';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }



  
  



  

  /*
  document.getElementById("train-btn").addEventListener("click", function () {
    const table = document.getElementById("resultsTable");
    const rows = table.querySelectorAll("tbody tr");
  
    const data = [];
  
    rows.forEach(row => {
      const cells = row.querySelectorAll("td");
      if (cells.length === 15) {
        data.push({
          id: cells[0].textContent.trim(),
          timestamp: cells[1].textContent.trim(),
          ct_src_dport_ltm: cells[2].textContent.trim(),
          rate: cells[3].textContent.trim(),
          dwin: cells[4].textContent.trim(),
          dload: cells[5].textContent.trim(),
          swin: cells[6].textContent.trim(),
          ct_dst_sport_ltm: cells[7].textContent.trim(),
          ct_state_ttl: cells[8].textContent.trim(),
          sttl: cells[9].textContent.trim(),
          src: cells[10].textContent.trim(),
          proto: cells[11].textContent.trim(),
          state: cells[12].textContent.trim(),
          mse: cells[13].textContent.trim(),
          result: cells[14].textContent.trim()
        });
      }
    });
  
    fetch("/save_csv/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken")
      },
      body: JSON.stringify({ data: data })
    })
    .then(response => response.json())
    .then(result => {
      alert("CSV saved successfully at: " + result.file_path);
    })
    .catch(error => {
      console.error("Error:", error);
      alert("Failed to save CSV");
    });
  });
  
  // لجلب CSRF Token
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
    */




  document.getElementById("train-btn").addEventListener("click", function () {
    const table = document.getElementById("resultsTable");
    const rows = table.querySelectorAll("tbody tr");
    const data = [];
  
    rows.forEach((row) => {
      const cells = row.querySelectorAll("td");
      if (cells.length === 15) {
        const rowData = {
          row_index: cells[0].innerText,
          timestamp: cells[1].innerText,
          ct_src_dport_ltm: cells[2].innerText,
          rate: cells[3].innerText,
          dwin: cells[4].innerText,
          dload: cells[5].innerText,
          swin: cells[6].innerText,
          ct_dst_sport_ltm: cells[7].innerText,
          ct_state_ttl: cells[8].innerText,
          sttl: cells[9].innerText,
          src: cells[10].innerText,
          proto: cells[11].innerText,
          state:cells[12].innerText,
          mse: cells[13].innerText,
          result: cells[14].innerText,
        };
        data.push(rowData);
      }
    });
  
    // Show loader
    Swal.fire({
      title: 'Please wait...',
      text: 'Sending data for training...',
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      }
    });
  
    fetch("/save_csv/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ data: data }),
    })
    .then((response) => response.json())
    .then((result) => {
      Swal.close(); // Close loading dialog
  
      if (result.status === "success") {
        Swal.fire({
          icon: 'success',
          title: '🎉 Training Successful!',
          html: '<b>Your data has been sent to FastAPI and training is complete.</b>',
          confirmButtonColor: '#28a745',
          confirmButtonText: 'Great!',
          showClass: {
            popup: 'animate__animated animate__fadeInDown'
          },
          hideClass: {
            popup: 'animate__animated animate__fadeOutUp'
          }
        });
      } else if (result.status === "partial_success") {
        Swal.fire({
          icon: 'warning',
          title: '⚠️ Partial Success',
          html: 'The data was saved locally, but could <b>not be sent to FastAPI</b>.',
          confirmButtonColor: '#ffc107',
          confirmButtonText: 'Got it',
          showClass: {
            popup: 'animate__animated animate__fadeInDown'
          },
          hideClass: {
            popup: 'animate__animated animate__fadeOutUp'
          }
        });
    } else {
        Swal.fire({
          icon: 'error',
          title: '❌ Failed to Process',
          text: 'An unexpected error occurred during the operation.',
          confirmButtonColor: '#dc3545',
          confirmButtonText: 'OK',
          showClass: {
            popup: 'animate__animated animate__fadeInDown'
          },
          hideClass: {
            popup: 'animate__animated animate__fadeOutUp'
          }
        });
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      Swal.close();
      Swal.fire({
        icon: 'error',
        title: '🔌 Connection Error',
        html: 'We couldn’t connect to the FastAPI server.<br>Please check your connection or server status.',
        confirmButtonColor: '#6c757d',
        confirmButtonText: 'Understood',
        showClass: {
          popup: 'animate__animated animate__fadeInDown'
        },
        hideClass: {
          popup: 'animate__animated animate__fadeOutUp'
        }
      });
    });
  });
  
  // CSRF helper
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }