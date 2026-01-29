/* General Styles */
body {
    font-family: 'Arial', sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f9f9f9;
    color: #333;
    line-height: 1.6;
}

header {
    background: #35424a;
    color: #ffffff;
    padding: 20px 0;
    text-align: center;
    border-bottom: 5px solid #45a049;
}

header h1 {
    margin: 0;
    font-size: 2.5rem;
}

nav ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    justify-content: center;
    gap: 20px;
}

nav ul li {
    display: inline;
}

nav ul li a {
    color: #ffffff;
    text-decoration: none;
    font-size: 1.2rem;
    padding: 10px 15px;
    border-radius: 5px;
    transition: background-color 0.3s ease;
}

nav ul li.active a {
    background-color: #45a049;
    font-weight: bold;
}

nav ul li a:hover {
    background-color: #0056b3;
}

/* Container chính */
.container {
    width: 1000px; /* Chiều rộng cố định */
    margin: 0 auto; /* Căn giữa container */
    padding: 10px; /* Giảm padding */
    background-color: #f9f9f9; /* Màu nền nhạt */
    border-radius: 10px; /* Bo góc container */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Đổ bóng nhẹ */
}

/* Form Styles */
form {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

form label {
    font-weight: bold;
}

form input, form textarea {
    padding: 10px;
    font-size: 1rem;
    border: 1px solid #cccccc;
    border-radius: 5px;
    width: 100%; /* Ensure inputs take full width of the container */
    box-sizing: border-box;
}

form textarea {
    resize: vertical;
}

form button {
    align-self: flex-start;
    background-color: #45a049;
    color: white;
    border: none;
    padding: 10px 15px;
    font-size: 1rem;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

form button:hover {
    background-color: #3c8c3c;
}

/* Buttons */
.button {
    background-color: #007bff;
    color: #fff;
    border: none;
    padding: 8px 12px; /* Giảm padding */
    font-size: 14px; /* Kích thước chữ nhỏ hơn */
    border-radius: 5px;
    cursor: pointer;
    text-decoration: none;
}

.button:hover {
    background-color: #0056b3;
}

.button-danger {
    background-color: #dc3545;
    color: #fff;
    border: none;
    padding: 8px 12px; /* Giảm padding */
    font-size: 14px; /* Kích thước chữ nhỏ hơn */
    border-radius: 5px;
    cursor: pointer;
}

.button-danger:hover {
    background-color: #c82333;
}

/* Nút với icon */
.button-icon {
    background-color: transparent;
    border: none;
    color: #007bff;
    font-size: 16px;
    cursor: pointer;
    padding: 5px;
    text-decoration: none;
}

.button-icon:hover {
    color: #0056b3;
}

.button-icon i {
    font-size: 18px;
}

/* Nút Edit Client */
.button-icon {
    background-color: transparent;
    border: none;
    color: #007bff;
    font-size: 16px;
    cursor: pointer;
    padding: 5px;
    text-decoration: none;
}

.button-icon:hover {
    color: #0056b3;
}

/* Nút Delete Client */
.button-icon.button-danger {
    color: #dc3545;
}

.button-icon.button-danger:hover {
    color: #c82333;
}

/* Nút Delete với icon */
.button-icon.button-danger {
    color: #dc3545;
}

.button-icon.button-danger:hover {
    color: #c82333;
}

/* Icon Buttons */
.icon-button {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 18px;
    color: #007bff;
    margin: 0 5px;
}

.icon-button:hover {
    color: #0056b3;
}

.icon-button.delete-button {
    color: #dc3545;
}

.icon-button.delete-button:hover {
    color: #a71d2a;
}

/* Liên kết chứa icon */
.icon-link {
    color: #007bff;
    font-size: 14px;
    margin-right: 5px;
    text-decoration: none;
}

.icon-link:hover {
    color: #0056b3;
}

/* Nút Delete */
.icon-link.icon-danger {
    color: #dc3545;
}

.icon-link.icon-danger:hover {
    color: #c82333;
}

/* Alerts */
.alerts {
    margin-top: 20px;
}

.alert {
    padding: 15px;
    margin-bottom: 10px;
    border: 1px solid transparent;
    border-radius: 4px;
    font-size: 1rem;
}

.alert-success {
    color: #3c763d;
    background-color: #dff0d8;
    border-color: #d6e9c6;
}

.alert-error {
    color: #a94442;
    background-color: #f2dede;
    border-color: #ebccd1;
}

/* Flash Messages */
#flash-messages {
    margin: 10px auto;
    max-width: 600px;
    width: 100%;
}

.flash-message {
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 5px;
    font-size: 14px;
    text-align: center;
    width: 100%;
    box-sizing: border-box;
}

.flash-message.success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.flash-message.error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.flash-message.info {
    background-color: #d1ecf1;
    color: #0c5460;
    border: 1px solid #bee5eb;
}

/* Bảng */
table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
    background-color: #fff;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

/* Header của bảng */
table thead th {
    background-color: #007bff;
    color: #fff;
    padding: 8px;
    text-align: left;
    font-size: 14px;
}

/* Dòng trong bảng */
table tbody tr {
    border-bottom: 1px solid #ddd;
}

table tbody tr:hover {
    background-color: #f1f1f1;
}

/* Ô trong bảng */
table td {
    padding: 8px;
    font-size: 14px;
    color: #333;
}

/* Footer */
footer {
    background: #35424a;
    color: #ffffff;
    text-align: center;
    padding: 10px 0;
    margin-top: 20px;
    border-top: 5px solid #45a049;
}

footer p {
    margin: 0;
    font-size: 1rem;
}

/* Dashboard Styles */
.dashboard-container {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    margin-top: 20px;
}

.dashboard-block {
    flex: 1;
    text-align: center;
    padding: 20px;
    background-color: #f4f4f4;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.dashboard-block h2 {
    font-size: 1.2rem;
    margin-bottom: 10px;
    color: #333;
}

.dashboard-number {
    font-size: 3.5rem;
    font-weight: bold;
    color: #45a049;
    margin: 0;
}

/* Allowed Domains Styling */
.allowed-domains {
    list-style: none;
    padding: 0;
    margin: 0;
}

/* Popup Notifications */
#popup-notifications {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.popup-notification {
    padding: 15px;
    border-radius: 5px;
    font-size: 1rem;
    color: white;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    animation: fadeOut 5s forwards;
}

.popup-notification.success {
    background-color: #45a049;
}

.popup-notification.error {
    background-color: #d9534f;
}

@keyframes fadeOut {
    0% {
        opacity: 1;
    }
    80% {
        opacity: 1;
    }
    100% {
        opacity: 0;
        transform: translateY(-20px);
    }
}

/* Action Row */
.action-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px; /* Giảm khoảng cách dưới */
}

/* Combobox và Filter */
.record-limit, .ip-filter {
    margin-right: 10px;
}

.record-limit select, .ip-filter input {
    padding: 5px;
    font-size: 14px;
    border: 1px solid #ccc;
    border-radius: 5px;
}

/* Phân trang */
.pagination {
    display: flex;
    justify-content: center;
    margin-top: 15px; /* Giảm khoảng cách trên */
}

.pagination button {
    background-color: #007bff;
    color: #fff;
    border: none;
    padding: 5px 10px; /* Giảm padding */
    margin: 0 5px;
    border-radius: 5px;
    cursor: pointer;
}

.pagination button.active {
    background-color: #0056b3;
    font-weight: bold;
}

.pagination button:hover {
    background-color: #0056b3;
}

/* Summary Row */
.summary-row {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    margin-bottom: 10px;
}

.summary-box {
    flex: 1;
    margin: 0 10px;
    padding: 20px;
    text-align: center;
    background-color: #f8f9fa;
    border: 1px solid #ddd;
    border-radius: 5px;
}

.summary-box h3 {
    margin-bottom: 5px;
    font-size: 16px;
    color: #333;
}

.summary-number {
    font-size: 60px;
    font-weight: bold;
    color: #007bff;
    margin: 0;
}

/* Clients Table */
#clients-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

#clients-table th {
    background-color: #007bff;
    color: white;
    font-weight: bold;
    padding: 10px;
    text-align: center;
}

#clients-table td {
    border: 1px solid #ddd;
    padding: 10px;
    text-align: center;
}

#clients-table tr.expired {
    background-color: #f8d7da;
    color: #721c24;
}

#clients-table tr.expired td {
    font-weight: bold;
}

/* Tô mờ trường input khi bị disabled */
.disabled-input {
    background-color: #f5f5f5;
    color: #a0a0a0;
    border: 1px solid #ccc;
    cursor: not-allowed;
}

/* Kiểu dành cho các trường readonly */
.readonly-input {
    background-color: #f9f9f9; /* Màu nền nhạt */
    color: #888; /* Màu chữ mờ */
    border: 1px solid #ccc; /* Viền nhạt */
    opacity: 0.7; /* Làm mờ toàn bộ textbox */
    pointer-events: none; /* Ngăn người dùng tương tác */
}

/* Chart Row */
.chart-row {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    margin-bottom: 10px;
}

.chart-box {
    flex: 1;
    margin: 0 10px;
    padding: 15px;
    text-align: center;
    background-color: #f8f9fa;
    border: 1px solid #ddd;
    border-radius: 5px;
    position: relative;
}

.chart-container {
    position: relative;
    display: inline-block;
    width: 100%;
    height: 100%;
}

.chart-container canvas {
    display: block;
    margin: 0 auto;
    max-width: 150px;
    max-height: 150px;
}

.chart-percentage {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 20px;
    font-weight: bold;
    color: #333;
}

/* Server Status Box */
.server-status-box {
    text-align: left;
    line-height: 1.5;
    font-size: 14px;
}

/* Highlight Header */
.highlight-header {
    margin-top: 5px;
    margin-bottom: 5px;
    font-size: 16px;
    font-weight: bold;
    color: #333;
    text-transform: uppercase;
    border-bottom: 2px solid #007bff;
    padding-bottom: 5px;
}

/* Squid Status Box */
.squid-status-box {
    text-align: left;
    line-height: 1.2;
    padding: 10px;
    font-size: 8px;
}

/* Bọc ô input và icon */
.input-with-icon {
    position: relative;
    display: flex;
    align-items: center;
}

.input-with-icon input {
    width: 100%;
    padding-right: 30px;
}

.input-with-icon i {
    position: absolute;
    right: 10px;
    color: #ccc;
    font-size: 16px;
    pointer-events: none;
}

/* Combobox để chọn số lượng record */
.record-limit {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    margin-bottom: 10px;
}

.record-limit label {
    margin-right: 10px;
    font-size: 14px;
    color: #333;
}

.record-limit select {
    padding: 5px 10px;
    font-size: 14px;
    border: 1px solid #ccc;
    border-radius: 5px;
}

/* Phân trang */
.pagination {
    display: flex;
    justify-content: center;
    margin-top: 15px;
}

.pagination button {
    background-color: #007bff;
    color: #fff;
    border: none;
    padding: 5px 10px;
    margin: 0 5px;
    border-radius: 5px;
    cursor: pointer;
}

.pagination button.active {
    background-color: #0056b3;
    font-weight: bold;
}

.pagination button:hover {
    background-color: #0056b3;
}

/* Nút sắp xếp */
.sort-button {
    background: none;
    border: none;
    color: #fff;
    cursor: pointer;
    font-size: 12px;
    margin-left: 5px;
    padding: 0;
    display: inline-flex;
    align-items: center;
}

.sort-button i {
    font-size: 10px;
}

.sort-button:hover {
    color: #007bff;
}

/* Container của menu */
.tab-menu {
    display: flex;
    justify-content: center; /* Căn giữa menu */
    background-color: #007bff; /* Màu nền xanh dương */
    padding: 10px 0; /* Khoảng cách trên dưới */
    border-radius: 8px; /* Bo góc menu */
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Đổ bóng nhẹ */
}

/* Các mục trong menu */
.tab-item {
    text-decoration: none; /* Loại bỏ gạch chân */
    color: #fff; /* Màu chữ trắng */
    font-size: 16px; /* Kích thước chữ */
    font-weight: 500; /* Đậm vừa */
    padding: 10px 20px; /* Khoảng cách trong */
    margin: 0 5px; /* Khoảng cách giữa các tab */
    border-radius: 5px; /* Bo góc từng tab */
    transition: all 0.3s ease; /* Hiệu ứng chuyển đổi */
    display: flex;
    align-items: center; /* Căn giữa icon và văn bản */
    gap: 8px; /* Khoảng cách giữa icon và văn bản */
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Đổ bóng 3D */
}

/* Hiệu ứng hover */
.tab-item:hover {
    background-color: #0056b3; /* Màu nền khi hover */
    color: #e0e0e0; /* Màu chữ khi hover */
    transform: translateY(-2px); /* Hiệu ứng nổi lên */
    box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2); /* Đổ bóng mạnh hơn */
}

/* Tab đang active */
.tab-item.active {
    background-color: #ffc107; /* Màu vàng nổi bật */
    color: #000; /* Màu chữ đen để dễ đọc */
    font-weight: bold; /* Chữ đậm hơn */
    box-shadow: 0 6px 10px rgba(0, 0, 0, 0.3); /* Đổ bóng mạnh hơn */
    transform: translateY(-2px); /* Hiệu ứng nổi lên */
    border: 2px solid #ff9800; /* Viền nổi bật */
}

/* Hiệu ứng hover cho tab đang active */
.tab-item.active:hover {
    background-color: #ffca28; /* Màu vàng sáng hơn khi hover */
    color: #000; /* Giữ màu chữ đen */
}

/* Icon trong tab */
.tab-item i {
    font-size: 18px; /* Kích thước icon */
}