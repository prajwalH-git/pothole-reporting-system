let map, markersLayer;

async function adminLogin() {
  const username = document.getElementById('adminUser').value;
  const password = document.getElementById('adminPass').value;

  const res = await fetch('/api/admin/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, password})
  });
  const data = await res.json();

  if (data.status === "ok") {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('adminPanel').style.display = 'block';
    initMap();
    loadPotholes();
  } else {
    alert("❌ Invalid credentials");
  }
}

async function loadPotholes() {
  const res = await fetch('/api/admin/potholes');
  const potholes = await res.json();
  renderTable(potholes);
  plotMarkers(potholes);
}

function renderTable(potholes) {
  const tbody = document.querySelector('#potholeTable tbody');
  tbody.innerHTML = '';
  potholes.forEach(p => {
    tbody.innerHTML += `
      <tr>
        <td>${p.title}</td>
        <td>${p.description}</td>
        <td>${p.severity}</td>
        <td>${p.reported_by}</td>
        <td>${p.lat || 'N/A'}</td>
        <td>${p.lon || 'N/A'}</td>
        <td>${new Date(p.reported_at).toLocaleString()}</td>
        <td>${p.photo_filename ? `<img src="/uploads/${p.photo_filename}" width="80">` : 'N/A'}</td>
      </tr>`;
  });
}

function initMap() {
  map = L.map('map').setView([12.9716, 77.5946], 11);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);
  markersLayer = L.layerGroup().addTo(map);
}

function plotMarkers(potholes) {
  markersLayer.clearLayers();
  potholes.forEach(p => {
    if (p.lat && p.lon) {
      const marker = L.marker([p.lat, p.lon]).addTo(markersLayer);
      marker.bindPopup(`
        <b>${p.title}</b><br>
        ${p.description}<br>
        Severity: ${p.severity}<br>
        Reporter: ${p.reported_by}<br>
        ${p.photo_filename ? `<img src="/uploads/${p.photo_filename}" width="150">` : ''}
      `);
    }
  });
}

function logout() {
  location.reload();
}
