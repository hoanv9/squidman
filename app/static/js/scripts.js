document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-client');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const clientId = this.dataset.clientId;
            const confirmation = confirm('Are you sure you want to delete this client?');
            if (!confirmation) {
                event.preventDefault();
            }
        });
    });

    const bulkDeleteButton = document.getElementById('bulk-delete');
    if (bulkDeleteButton) {
        bulkDeleteButton.addEventListener('click', function() {
            const selectedClients = document.querySelectorAll('input[name="client_ids"]:checked');
            if (selectedClients.length === 0) {
                alert('Please select at least one client to delete.');
                event.preventDefault();
            } else {
                const confirmation = confirm('Are you sure you want to delete the selected clients?');
                if (!confirmation) {
                    event.preventDefault();
                }
            }
        });
    }

    const applyConfigButton = document.getElementById('apply-config');
    if (applyConfigButton) {
        applyConfigButton.addEventListener('click', function() {
            const confirmation = confirm('Are you sure you want to apply these configurations to Squid? This will overwrite the existing configurations.');
            if (!confirmation) {
                event.preventDefault();
            }
        });
    }

    // Automatically remove popup notifications after 5 seconds
    const notifications = document.querySelectorAll('.popup-notification');
    notifications.forEach((notification) => {
        setTimeout(() => {
            notification.remove();
        }, 5000);
    });

    // Biểu đồ CPU
    const cpuCtx = document.getElementById('cpuGauge').getContext('2d');
    const cpuGauge = new Chart(cpuCtx, {
        type: 'doughnut',
        data: {
            labels: ['Used', 'Free'],
            datasets: [{
                data: [70, 30],
                backgroundColor: ['#ff6384', '#e0e0e0'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            cutout: '80%',
            plugins: {
                doughnutlabel: {
                    labels: [
                        {
                            text: '70%',
                            font: {
                                size: '20'
                            }
                        },
                        {
                            text: 'CPU'
                        }
                    ]
                }
            }
        }
    });

    // Biểu đồ RAM
    const ramCtx = document.getElementById('ramGauge').getContext('2d');
    const ramGauge = new Chart(ramCtx, {
        type: 'doughnut',
        data: {
            labels: ['Used', 'Free'],
            datasets: [{
                data: [50, 50],
                backgroundColor: ['#36a2eb', '#e0e0e0'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            cutout: '80%',
            plugins: {
                doughnutlabel: {
                    labels: [
                        {
                            text: '50%',
                            font: {
                                size: '20'
                            }
                        },
                        {
                            text: 'RAM'
                        }
                    ]
                }
            }
        }
    });

    // Làm mới dữ liệu mỗi 5 giây
    setInterval(refreshStats, 5000);
});

// Function to show popup notifications
function showPopupNotification(message, type = 'success') {
    const container = document.getElementById('popup-notifications');

    // Create a new notification element
    const notification = document.createElement('div');
    notification.className = `popup-notification ${type}`;
    notification.textContent = message;

    // Append the notification to the container
    container.appendChild(notification);

    // Remove the notification after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Ensure forms with GET method are not blocked
document.querySelectorAll('form').forEach((form) => {
    form.addEventListener('submit', (event) => {
        if (form.method.toLowerCase() === 'get') {
            // Allow default behavior for GET forms
            return;
        }

        // Handle POST forms (e.g., AJAX submission)
        event.preventDefault();
        const formData = new FormData(form);
        const action = form.action;

        fetch(action, {
            method: form.method,
            body: formData,
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Failed to process the request.');
                }
                return response.json();
            })
            .then((data) => {
                showPopupNotification(data.message, data.type);
            })
            .catch((error) => {
                showPopupNotification('An error occurred. Please try again.', 'error');
            });
    });
});

// Sort table function
function sortTable(columnClass) {
    const table = document.getElementById('clients-table');
    const rows = Array.from(table.querySelectorAll('tbody .client-row'));
    const isNumeric = columnClass === 'days-remaining';
    const isDate = columnClass === 'date-added' || columnClass === 'expiration-date';

    rows.sort((a, b) => {
        const aValue = a.querySelector(`.${columnClass}`).textContent.trim();
        const bValue = b.querySelector(`.${columnClass}`).textContent.trim();

        if (isNumeric) {
            return parseInt(aValue) - parseInt(bValue);
        } else if (isDate) {
            return new Date(aValue) - new Date(bValue);
        } else {
            return aValue.localeCompare(bValue);
        }
    });

    // Reverse order if already sorted
    if (table.dataset.sortedColumn === columnClass && table.dataset.sortOrder === 'asc') {
        rows.reverse();
        table.dataset.sortOrder = 'desc';
    } else {
        table.dataset.sortOrder = 'asc';
    }

    table.dataset.sortedColumn = columnClass;

    // Update table rows order
    const tbody = table.querySelector('tbody');
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
}

// Function to refresh system stats
function refreshStats() {
    fetch('/api/system_stats') // Gọi API để lấy dữ liệu CPU, RAM và Bandwidth
        .then(response => response.json())
        .then(data => {
            createCpuChart(data.cpu_percent);
            createRamChart(data.ram_percent);
            document.getElementById('bandwidth').innerText = `${data.bandwidth}`;
        })
        .catch(error => console.error('Error fetching system stats:', error));
}

// Function to confirm delete selected clients
function confirmDeleteSelected() {
    // Lấy danh sách các checkbox được chọn
    const selected = document.querySelectorAll('input[name="selected_clients"]:checked');
    
    // Nếu không có checkbox nào được chọn, hiển thị thông báo và ngăn việc gửi form
    if (selected.length === 0) {
        alert('Please select at least one client to delete.');
        return false;
    }

    // Hiển thị hộp thoại xác nhận
    return confirm('Are you sure you want to delete the selected clients?');
}