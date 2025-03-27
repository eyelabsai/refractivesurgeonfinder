class MapHandler {
    constructor() {
        this.map = null;
        this.markers = [];
    }

    initializeMap(elementId, center = [20, 0], zoom = 2) {
        this.map = L.map(elementId).setView(center, zoom);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
    }

    clearMarkers() {
        this.markers.forEach(marker => marker.remove());
        this.markers = [];
    }

    addMarker(lat, lng, popupContent) {
        const marker = L.marker([lat, lng])
            .bindPopup(popupContent)
            .addTo(this.map);
        this.markers.push(marker);
        return marker;
    }

    centerOnMarkers() {
        if (this.markers.length > 0) {
            const group = new L.featureGroup(this.markers);
            this.map.fitBounds(group.getBounds());
        }
    }
} 