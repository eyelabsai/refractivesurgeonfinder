<?php
/**
 * Plugin Name: Refractive Surgeon Finder
 * Plugin URI: https://yourwebsite.com/refractive-surgeon-finder
 * Description: A plugin to find refractive surgeons by ZIP code
 * Version: 1.0.0
 * Author: Your Name
 * Author URI: https://yourwebsite.com
 * Text Domain: refractive-surgeon-finder
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('RSF_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('RSF_PLUGIN_URL', plugin_dir_url(__FILE__));

// Enqueue scripts and styles
function rsf_enqueue_scripts() {
    // Enqueue Leaflet CSS and JS
    wp_enqueue_style('leaflet-css', 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.css');
    wp_enqueue_script('leaflet-js', 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.js', array(), '1.7.1', true);
    
    // Enqueue Leaflet marker cluster
    wp_enqueue_style('leaflet-markercluster-css', 'https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css');
    wp_enqueue_style('leaflet-markercluster-default-css', 'https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css');
    wp_enqueue_script('leaflet-markercluster-js', 'https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js', array('leaflet-js'), '1.4.1', true);
    
    // Enqueue our custom CSS and JS
    wp_enqueue_style('rsf-style', RSF_PLUGIN_URL . 'css/style.css');
    wp_enqueue_script('surgeons-data', RSF_PLUGIN_URL . 'js/surgeons-data.js', array(), '1.0.0', true);
    wp_enqueue_script('rsf-map-handler', RSF_PLUGIN_URL . 'js/map-handler.js', array('leaflet-js', 'surgeons-data'), '1.0.0', true);
    wp_enqueue_script('rsf-main', RSF_PLUGIN_URL . 'js/main.js', array('jquery', 'leaflet-js', 'surgeons-data', 'rsf-map-handler'), '1.0.0', true);
}
add_action('wp_enqueue_scripts', 'rsf_enqueue_scripts');

// Shortcode for the surgeon finder form
function rsf_search_form_shortcode() {
    ob_start();
    include RSF_PLUGIN_DIR . 'templates/search-form.php';
    return ob_get_clean();
}
add_shortcode('surgeon_finder_form', 'rsf_search_form_shortcode');

// Shortcode for the surgeon results
function rsf_results_shortcode() {
    ob_start();
    include RSF_PLUGIN_DIR . 'templates/results.php';
    return ob_get_clean();
}
add_shortcode('surgeon_finder_results', 'rsf_results_shortcode');

// Shortcode for the world map
function rsf_world_map_shortcode() {
    ob_start();
    include RSF_PLUGIN_DIR . 'templates/world-map.php';
    return ob_get_clean();
}
add_shortcode('surgeon_world_map', 'rsf_world_map_shortcode'); 