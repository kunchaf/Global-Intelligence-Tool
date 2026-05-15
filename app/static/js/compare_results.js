(function () {
    const script = document.getElementById("compare-data");
    const mapEl = document.getElementById("map");
    if (!script || !mapEl) return;

    let payload;
    try {
        payload = JSON.parse(script.textContent);
    } catch (e) {
        console.error(e);
        return;
    }

    const rows = payload.rows || [];
    const map = L.map("map").setView([20, 0], 2);
    const markersLayer = L.layerGroup().addTo(map);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap",
    }).addTo(map);

    const bounds = [];
    for (const row of rows) {
        if (row.error) continue;
        const lat = row.latitude;
        const lng = row.longitude;
        if (typeof lat !== "number" || typeof lng !== "number") continue;
        const label = row.country || row.country_code || "";
        const m = L.marker([lat, lng]).bindPopup(
            "<strong>" + String(label) + "</strong><br>" + String(row.country_code || "")
        );
        markersLayer.addLayer(m);
        bounds.push([lat, lng]);
    }

    if (bounds.length === 1) {
        map.setView(bounds[0], 4);
    } else if (bounds.length > 1) {
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 5 });
    }
})();
