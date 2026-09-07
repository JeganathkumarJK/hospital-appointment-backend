ADMIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CarePilot Backend - Database & User Management</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090d16;
      --card-bg: #111827;
      --card-border: #1f293d;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --accent: #38bdf8;
      --danger: #ef4444;
      --danger-hover: #dc2626;
      --success: #10b981;
      --warning: #f59e0b;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      min-height: 100vh;
      padding: 24px;
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      padding-bottom: 24px;
      border-bottom: 1px solid var(--card-border);
      margin-bottom: 24px;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .logo-icon {
      width: 44px;
      height: 44px;
      background: linear-gradient(135deg, var(--primary), var(--accent));
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      font-weight: bold;
      color: white;
      box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
    }
    .brand h1 { font-size: 20px; font-weight: 700; color: #fff; }
    .brand p { font-size: 13px; color: var(--text-muted); }
    .header-links { display: flex; gap: 12px; align-items: center; }
    .btn {
      padding: 9px 16px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      text-decoration: none;
    }
    .btn-primary { background: var(--primary); color: #fff; }
    .btn-primary:hover { background: var(--primary-hover); }
    .btn-secondary { background: #1e293b; color: #cbd5e1; border-color: var(--card-border); }
    .btn-secondary:hover { background: #334155; color: #fff; }
    .btn-danger { background: rgba(239, 68, 68, 0.15); color: #f87171; border-color: rgba(239, 68, 68, 0.3); }
    .btn-danger:hover { background: var(--danger); color: white; }
    .btn-sm { padding: 5px 10px; font-size: 12px; }

    /* Stats bar */
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }
    .stat-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .stat-label { font-size: 12px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }
    .stat-val { font-size: 26px; font-weight: 700; color: #fff; }

    /* Tabs */
    .tabs {
      display: flex;
      gap: 8px;
      border-bottom: 1px solid var(--card-border);
      margin-bottom: 20px;
    }
    .tab-btn {
      padding: 12px 18px;
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      transition: all 0.2s;
    }
    .tab-btn.active {
      color: var(--accent);
      border-bottom-color: var(--accent);
    }

    /* Controls bar */
    .controls {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 12px;
    }
    .search-box {
      padding: 9px 14px;
      background: #1e293b;
      border: 1px solid var(--card-border);
      border-radius: 8px;
      color: #fff;
      font-size: 13px;
      min-width: 260px;
    }
    .search-box:focus { outline: 1px solid var(--accent); }

    /* Tables */
    .table-container {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      overflow-x: auto;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 13px;
    }
    th {
      padding: 14px 16px;
      background: rgba(30, 41, 59, 0.5);
      color: #94a3b8;
      font-weight: 600;
      border-bottom: 1px solid var(--card-border);
    }
    td {
      padding: 14px 16px;
      border-bottom: 1px solid var(--card-border);
      color: #e2e8f0;
    }
    tr:last-child td { border-bottom: none; }
    tr:hover td { background: rgba(255, 255, 255, 0.02); }

    /* Badges */
    .badge {
      padding: 3px 8px;
      border-radius: 9999px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      display: inline-block;
    }
    .badge-patient { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
    .badge-admin { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
    .badge-success { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-failed { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }

    /* Toast */
    #toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #1e293b;
      border: 1px solid var(--accent);
      color: #fff;
      padding: 12px 20px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      display: none;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      z-index: 1000;
    }
    .tab-content { display: none; }
    .tab-content.active { display: block; }
  </style>
</head>
<body>

  <div class="header">
    <div class="brand">
      <div class="logo-icon">+</div>
      <div>
        <h1>CarePilot Backend Database & Operations Center</h1>
        <p>Live User Management, Real-time Sign-in Logs & Data Control</p>
      </div>
    </div>
    <div class="header-links">
      <a href="/docs" target="_blank" class="btn btn-secondary">Swagger UI Docs</a>
      <button onclick="refreshAll()" class="btn btn-primary">Refresh Data</button>
    </div>
  </div>

  <div class="stats-grid">
    <div class="stat-card">
      <span class="stat-label">Total Users</span>
      <span class="stat-val" id="stat-users">-</span>
    </div>
    <div class="stat-card">
      <span class="stat-label">Registered Patients</span>
      <span class="stat-val" id="stat-patients">-</span>
    </div>
    <div class="stat-card">
      <span class="stat-label">Sign-in Events</span>
      <span class="stat-val" id="stat-logins">-</span>
    </div>
    <div class="stat-card">
      <span class="stat-label">Appointments</span>
      <span class="stat-val" id="stat-appointments">-</span>
    </div>
  </div>

  <div class="tabs">
    <button class="tab-btn active" onclick="switchTab('tab-users')">Registered Users & Sign-Ups</button>
    <button class="tab-btn" onclick="switchTab('tab-logins')">Sign-In & Login Activity Logs</button>
    <button class="tab-btn" onclick="switchTab('tab-appointments')">Appointments Management</button>
  </div>

  <!-- TAB 1: USERS -->
  <div id="tab-users" class="tab-content active">
    <div class="controls">
      <input type="text" id="search-users" class="search-box" placeholder="Search by name, email, ID..." oninput="filterUsers()">
      <div>
        <span style="font-size: 13px; color: var(--text-muted);">Click Delete next to any user to permanently remove them from the database.</span>
      </div>
    </div>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>User ID</th>
            <th>Full Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Role</th>
            <th>Joined</th>
            <th>Last Login</th>
            <th>Login Count</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody id="users-tbody">
          <tr><td colspan="9" style="text-align: center; color: var(--text-muted);">Loading user records...</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- TAB 2: LOGIN LOGS -->
  <div id="tab-logins" class="tab-content">
    <div class="controls">
      <input type="text" id="search-logins" class="search-box" placeholder="Search login activity..." oninput="filterLogins()">
      <button onclick="clearAllLoginLogs()" class="btn btn-danger btn-sm">Clear All Login Logs</button>
    </div>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Email / Identifier</th>
            <th>User Name</th>
            <th>Role</th>
            <th>Status</th>
            <th>IP Address</th>
            <th>User Agent</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody id="logins-tbody">
          <tr><td colspan="8" style="text-align: center; color: var(--text-muted);">Loading login logs...</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- TAB 3: APPOINTMENTS -->
  <div id="tab-appointments" class="tab-content">
    <div class="controls">
      <input type="text" id="search-appointments" class="search-box" placeholder="Search appointments..." oninput="filterAppointments()">
      <span style="font-size: 13px; color: var(--text-muted);">Delete test or outdated appointments.</span>
    </div>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Apt ID</th>
            <th>Patient</th>
            <th>Doctor</th>
            <th>Department</th>
            <th>Date & Time</th>
            <th>Risk Level</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody id="appointments-tbody">
          <tr><td colspan="8" style="text-align: center; color: var(--text-muted);">Loading appointments...</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <div id="toast"></div>

  <script>
    let allUsers = [];
    let allLogins = [];
    let allAppointments = [];

    function showToast(msg, isError = false) {
      const t = document.getElementById('toast');
      t.innerText = msg;
      t.style.borderColor = isError ? '#ef4444' : '#38bdf8';
      t.style.display = 'block';
      setTimeout(() => { t.style.display = 'none'; }, 4000);
    }

    function switchTab(tabId) {
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      event.target.classList.add('active');
      document.getElementById(tabId).classList.add('active');
    }

    async function loadUsers() {
      try {
        const res = await fetch('/auth/users');
        allUsers = await res.json();
        document.getElementById('stat-users').innerText = allUsers.length;
        document.getElementById('stat-patients').innerText = allUsers.filter(u => u.role === 'patient').length;
        renderUsers(allUsers);
      } catch (err) {
        document.getElementById('users-tbody').innerHTML = `<tr><td colspan="9" style="color: #f87171; text-align: center;">Failed to load users: ${err.message}</td></tr>`;
      }
    }

    function renderUsers(users) {
      const tbody = document.getElementById('users-tbody');
      if (!users.length) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--text-muted);">No users found.</td></tr>`;
        return;
      }
      tbody.innerHTML = users.map(u => `
        <tr>
          <td><strong>${u.id}</strong></td>
          <td>${u.fullName}</td>
          <td>${u.email}</td>
          <td>${u.phone || '—'}</td>
          <td><span class="badge ${u.role === 'admin' ? 'badge-admin' : 'badge-patient'}">${u.role}</span></td>
          <td>${u.joined.split(' ')[0]}</td>
          <td>${u.lastLogin || 'Never'}</td>
          <td>${u.loginCount || 0}</td>
          <td>
            <button class="btn btn-danger btn-sm" onclick="deleteUser('${u.id}', '${u.fullName}')">Delete</button>
          </td>
        </tr>
      `).join('');
    }

    function filterUsers() {
      const q = document.getElementById('search-users').value.toLowerCase();
      const filtered = allUsers.filter(u =>
        u.id.toLowerCase().includes(q) ||
        u.fullName.toLowerCase().includes(q) ||
        u.email.toLowerCase().includes(q)
      );
      renderUsers(filtered);
    }

    async function deleteUser(id, name) {
      if (!confirm(`Are you sure you want to permanently delete user '${name}' (${id})? This will also remove their appointments and waitlist records.`)) {
        return;
      }
      try {
        const res = await fetch(`/auth/users/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (res.ok) {
          showToast(data.message || 'User deleted successfully.');
          refreshAll();
        } else {
          showToast(data.detail || 'Failed to delete user', true);
        }
      } catch (err) {
        showToast(err.message, true);
      }
    }

    async function loadLogins() {
      try {
        const res = await fetch('/auth/login-history');
        allLogins = await res.json();
        document.getElementById('stat-logins').innerText = allLogins.length;
        renderLogins(allLogins);
      } catch (err) {
        document.getElementById('logins-tbody').innerHTML = `<tr><td colspan="8" style="color: #f87171; text-align: center;">Failed to load login history: ${err.message}</td></tr>`;
      }
    }

    function renderLogins(logs) {
      const tbody = document.getElementById('logins-tbody');
      if (!logs.length) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted);">No login events recorded yet.</td></tr>`;
        return;
      }
      tbody.innerHTML = logs.map(l => `
        <tr>
          <td>${l.timestamp}</td>
          <td><strong>${l.email}</strong></td>
          <td>${l.fullName || '—'}</td>
          <td><span class="badge ${l.role === 'admin' ? 'badge-admin' : 'badge-patient'}">${l.role}</span></td>
          <td><span class="badge ${l.status === 'SUCCESS' ? 'badge-success' : 'badge-failed'}">${l.status}</span></td>
          <td><code>${l.ipAddress || '—'}</code></td>
          <td style="max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${l.userAgent}">${l.userAgent || '—'}</td>
          <td>
            <button class="btn btn-danger btn-sm" onclick="deleteLoginLog(${l.id})">Delete</button>
          </td>
        </tr>
      `).join('');
    }

    function filterLogins() {
      const q = document.getElementById('search-logins').value.toLowerCase();
      const filtered = allLogins.filter(l =>
        l.email.toLowerCase().includes(q) ||
        (l.fullName && l.fullName.toLowerCase().includes(q)) ||
        l.status.toLowerCase().includes(q)
      );
      renderLogins(filtered);
    }

    async function deleteLoginLog(id) {
      try {
        const res = await fetch(`/auth/login-history/${id}`, { method: 'DELETE' });
        if (res.ok) {
          showToast(`Deleted log #${id}`);
          loadLogins();
        }
      } catch (err) {
        showToast(err.message, true);
      }
    }

    async function clearAllLoginLogs() {
      if (!confirm('Are you sure you want to clear all login logs?')) return;
      try {
        const res = await fetch('/auth/login-history', { method: 'DELETE' });
        const data = await res.json();
        showToast(data.message || 'Cleared all logs');
        loadLogins();
      } catch (err) {
        showToast(err.message, true);
      }
    }

    async function loadAppointments() {
      try {
        const res = await fetch('/appointments');
        allAppointments = await res.json();
        document.getElementById('stat-appointments').innerText = allAppointments.length;
        renderAppointments(allAppointments);
      } catch (err) {
        document.getElementById('appointments-tbody').innerHTML = `<tr><td colspan="8" style="color: #f87171; text-align: center;">Failed to load appointments: ${err.message}</td></tr>`;
      }
    }

    function renderAppointments(apts) {
      const tbody = document.getElementById('appointments-tbody');
      if (!apts.length) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted);">No appointments found.</td></tr>`;
        return;
      }
      tbody.innerHTML = apts.map(a => `
        <tr>
          <td><strong>${a.id}</strong></td>
          <td>${a.patient} <br><span style="font-size: 11px; color: var(--text-muted);">${a.patientId}</span></td>
          <td>${a.doctor}</td>
          <td>${a.department}</td>
          <td>${a.date} at ${a.time}</td>
          <td><span class="badge ${a.risk === 'HIGH' ? 'badge-failed' : a.risk === 'MEDIUM' ? 'badge-admin' : 'badge-success'}">${a.risk} (${a.probability}%)</span></td>
          <td><strong>${a.status}</strong></td>
          <td>
            <button class="btn btn-danger btn-sm" onclick="deleteAppointment('${a.id}')">Delete</button>
          </td>
        </tr>
      `).join('');
    }

    function filterAppointments() {
      const q = document.getElementById('search-appointments').value.toLowerCase();
      const filtered = allAppointments.filter(a =>
        a.id.toLowerCase().includes(q) ||
        a.patient.toLowerCase().includes(q) ||
        a.doctor.toLowerCase().includes(q)
      );
      renderAppointments(filtered);
    }

    async function deleteAppointment(id) {
      if (!confirm(`Permanently delete appointment ${id}?`)) return;
      try {
        const res = await fetch(`/appointments/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (res.ok) {
          showToast(data.message || 'Appointment deleted');
          loadAppointments();
        } else {
          showToast(data.detail || 'Failed to delete appointment', true);
        }
      } catch (err) {
        showToast(err.message, true);
      }
    }

    function refreshAll() {
      loadUsers();
      loadLogins();
      loadAppointments();
    }

    // Initial load
    refreshAll();
  </script>
</body>
</html>
"""
