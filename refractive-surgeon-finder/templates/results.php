<div id="results-container" class="results-container">
    <div id="map" class="map-container"></div>
    <div id="results-list" class="results-list">
        <h3>Search Results</h3>
        <div id="surgeons-list"></div>
    </div>
</div>

<script>
jQuery(document).ready(function($) {
    $('#search-form').on('submit', async function(e) {
        e.preventDefault();
        const zipCode = $('#zip-code').val();
        const radius = parseFloat($('#radius').val()) || 50;
        await searchSurgeons(zipCode, radius);
    });
});
</script> 