jQuery(document).ready(function($) {
    // Handle search form submission
    $('#surgeon-search-form').on('submit', function(e) {
        e.preventDefault();
        
        var formData = {
            'action': 'search_surgeons',
            'zip_code': $('#zip_code').val(),
            'radius': $('#radius').val()
        };

        $.ajax({
            url: surgeon_finder_ajax.ajax_url,
            type: 'POST',
            data: formData,
            success: function(response) {
                displayResults(response);
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
    });

    function displayResults(data) {
        var resultsHtml = '<h3>Found ' + data.results.length + ' surgeons:</h3>';
        resultsHtml += '<div class="surgeon-list">';
        
        data.results.forEach(function(surgeon) {
            resultsHtml += `
                <div class="surgeon-item">
                    <h4>${surgeon.name}</h4>
                    <p>Practice: ${surgeon.practice}<br>
                    Address: ${surgeon.address}<br>
                    Phone: ${surgeon.phone}<br>
                    Website: <a href="${surgeon.website}" target="_blank">${surgeon.website}</a><br>
                    Distance: ${surgeon.distance} miles</p>
                </div>
            `;
        });
        
        resultsHtml += '</div>';
        $('#search-results').html(resultsHtml);
        
        // Update map
        if (data.map_html) {
            $('#surgeon-map').html(data.map_html);
        }
    }
}); 