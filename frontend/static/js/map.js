let map = L.map('map').setView([37.5665, 126.9780], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19
}).addTo(map);

async function getRoute() {
    const start = document.getElementById('start').value.split(',').map(Number);
    const end = document.getElementById('end').value.split(',').map(Number);
    const disabledType = document.getElementById('disabledType').value;
    const res = await fetch('/api/predict-route', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({start, end, disabled_type: disabledType})
    });
    const data = await res.json();
    const latlngs = data.recommended_route;
    L.polyline(latlngs, {color: 'blue'}).addTo(map);
}
