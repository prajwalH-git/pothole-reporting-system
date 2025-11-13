let map;
let userMarker;

function initMap() {
  map = L.map('map').setView([12.9716, 77.5946], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap'
  }).addTo(map);
}

function getLocation() {
  if (!navigator.geolocation) {
    alert("Geolocation not supported.");
    return;
  }

  navigator.geolocation.getCurrentPosition(pos => {
    const lat = pos.coords.latitude;
    const lon = pos.coords.longitude;

    document.getElementById('lat').value = lat;
    document.getElementById('lon').value = lon;

    if (userMarker) {
      userMarker.setLatLng([lat, lon]);
    } else {
      userMarker = L.marker([lat, lon]).addTo(map)
        .bindPopup("📍 Your Location").openPopup();
    }

    map.setView([lat, lon], 15);
  }, err => {
    alert("Unable to get location: " + err.message);
  });
}

async function submitReport(e) {
  e.preventDefault();
  const form = document.getElementById('reportForm');
  const formData = new FormData(form);

  const res = await fetch('/api/report', { method: 'POST', body: formData });
  const data = await res.json();

  if (data.status === "success") {
    alert("✅ Pothole reported successfully!");
    form.reset();
    if (userMarker) map.removeLayer(userMarker);
  } else {
    alert("❌ Error: " + (data.message || "Failed to submit report"));
  }
}

window.onload = initMap;
