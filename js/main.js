document.addEventListener('DOMContentLoaded', function() {
    const mapHandler = new MapHandler();
    let currentSection = 'search';

    // Initialize the search map
    mapHandler.initializeMap('map');

    // Handle navigation
    document.getElementById('search-tab').addEventListener('click', function(e) {
        e.preventDefault();
        showSection('search');
    });

    document.getElementById('world-map-tab').addEventListener('click', function(e) {
        e.preventDefault();
        showSection('world-map');
    });

    // Handle search form submission
    document.getElementById('search-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const zipCode = document.getElementById('zip-code').value;
        const radius = document.getElementById('radius').value;
        searchSurgeons(zipCode, radius);
    });

    function showSection(sectionName) {
        document.getElementById('search-section').style.display = 
            sectionName === 'search' ? 'block' : 'none';
        document.getElementById('world-map-section').style.display = 
            sectionName === 'world-map' ? 'block' : 'none';

        if (sectionName === 'world-map' && !document.getElementById('world-map').hasChildNodes()) {
            initializeWorldMap();
        }
    }

    function searchSurgeons(zipCode, radius) {
        // This would normally be an API call, but for GitHub Pages we'll use the static data
        const results = filterSurgeonsByZipCode(surgeonsData, zipCode, radius);
        displayResults(results);
    }

    function displayResults(results) {
        const resultsContainer = document.getElementById('results-list');
        mapHandler.clearMarkers();

        if (results.length === 0) {
            resultsContainer.innerHTML = '<p>No surgeons found in this area.</p>';
            return;
        }

        let html = '<div class="list-group">';
        results.forEach(surgeon => {
            html += `
                <div class="list-group-item">
                    <h5>${surgeon.name}</h5>
                    <p>
                        Practice: ${surgeon.practice_name}<br>
                        Address: ${surgeon.address}<br>
                        Phone: ${surgeon.phone}<br>
                        Website: <a href="${surgeon.website}" target="_blank">${surgeon.website}</a>
                    </p>
                </div>
            `;

            const popupContent = `
                <b>${surgeon.name}</b><br>
                ${surgeon.practice_name}<br>
                ${surgeon.address}
            `;

            mapHandler.addMarker(
                surgeon.coordinates.lat,
                surgeon.coordinates.lng,
                popupContent
            );
        });
        html += '</div>';
        resultsContainer.innerHTML = html;
        mapHandler.centerOnMarkers();
    }

    function initializeWorldMap() {
        const worldMapHandler = new MapHandler();
        worldMapHandler.initializeMap('world-map');
        
        surgeonsData.forEach(surgeon => {
            const popupContent = `
                <b>${surgeon.name}</b><br>
                ${surgeon.practice_name}<br>
                ${surgeon.address}
            `;

            worldMapHandler.addMarker(
                surgeon.coordinates.lat,
                surgeon.coordinates.lng,
                popupContent
            );
        });
    }
}); 