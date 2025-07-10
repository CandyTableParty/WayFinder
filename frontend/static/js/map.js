
let map = L.map('map').setView([37.5665, 126.9780], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);

let currentPolyline = null;

async function getRoute() {
    const startInput = document.getElementById("start").value.trim();
    const endInput = document.getElementById("end").value.trim();
    const type = document.getElementById("disabledType").value;

    const startEl = document.getElementById("start");
    const endEl = document.getElementById("end");
    const start = [parseFloat(startEl.dataset.lat), parseFloat(startEl.dataset.lon)];
    const end = [parseFloat(endEl.dataset.lat), parseFloat(endEl.dataset.lon)];

    //const start = startInput.split(",").map(x => Number(x.trim()));
    //const end = endInput.split(",").map(x => Number(x.trim()));

    if (start.length !== 2 || end.length !== 2 || start.some(isNaN) || end.some(isNaN)) {
        alert("출발지와 도착지를 올바르게 입력하세요. 예: 37.5665,126.9780");
        return;
    }

    const requestData = {
        start,
        end,
        disabled_type: type
    };

    try {
        const response = await fetch("/api/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) throw new Error("서버 응답 실패");

        const data = await response.json();

        if (!data.route || !Array.isArray(data.route) || data.route.length === 0) {
            alert("경로가 비어있거나 잘못된 응답입니다.");
            return;
        }

        drawRoute(data.route);

    } catch (err) {
        console.error("예측 실패:", err);
        alert("경로 예측 중 오류가 발생했습니다.");
    }
}

function drawRoute(coords) {
    if (!Array.isArray(coords) || coords.length === 0) {
        console.error("📛 유효하지 않은 경로 데이터", coords);
        return;
    }

    if (currentPolyline) {
        map.removeLayer(currentPolyline);
    }

    currentPolyline = L.polyline(coords, { color: 'blue' }).addTo(map);
    map.fitBounds(currentPolyline.getBounds());
}



async function searchLocation(inputId) {
    const query = document.getElementById(inputId).value.trim();
    if (!query) {
        alert("검색할 장소명을 입력해주세요.");
        return;
    }

    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json`;
    try {
        const res = await fetch(url);
        const data = await res.json();
        if (!data || data.length === 0) {
            alert("검색 결과가 없습니다.");
            return;
        }

        const lat = parseFloat(data[0].lat).toFixed(6);
        const lon = parseFloat(data[0].lon).toFixed(6);
        //document.getElementById(inputId).value = `${lat},${lon}`;
        document.getElementById(inputId).dataset.lat = lat;
        document.getElementById(inputId).dataset.lon = lon;
    } catch (err) {
        console.error("주소 검색 실패:", err);
        alert("주소 검색 중 오류가 발생했습니다.");
    }
}

function useCurrentLocation() {
    if (!navigator.geolocation) {
        alert("브라우저가 위치 정보를 지원하지 않습니다.");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        async (position) => {
            const lat = position.coords.latitude.toFixed(6);
            const lon = position.coords.longitude.toFixed(6);

            const startInput = document.getElementById("start");
            startInput.dataset.lat = lat;
            startInput.dataset.lon = lon;

            // 역지오코딩으로 주소명 가져오기
            const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`;
            try {
                const res = await fetch(url);
                const data = await res.json();
                startInput.value = data.display_name || `${lat},${lon}`;
            } catch {
                startInput.value = `${lat},${lon}`; // 실패 시 fallback
            }
        },
        (error) => {
            console.error("위치 정보 오류:", error);
            alert("현재 위치를 가져올 수 없습니다. 브라우저 설정을 확인해주세요.");
        }
    );
}