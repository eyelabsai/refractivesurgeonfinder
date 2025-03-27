import pandas as pd
import folium
from folium.plugins import MarkerCluster
import webbrowser
import os

def create_world_surgeon_map():
    # Read the CSV with addresses and coordinates
    df = pd.read_csv('surgeons_with_addresses.csv')
    
    # Create a map centered roughly in the middle of the world
    m = folium.Map(location=[20, 0], zoom_start=2)
    
    # Create a marker cluster to handle many markers efficiently
    marker_cluster = MarkerCluster(name="Surgeons")
    
    # Add markers for each surgeon
    for _, surgeon in df.iterrows():
        try:
            # Parse coordinates
            coords = eval(str(surgeon['coordinates']))
            
            # Create popup content
            popup_html = f"""
                <b>{surgeon['name']}</b><br>
                Practice: {surgeon['practice_name']}<br>
                Address: {surgeon['address']}<br>
                Phone: {surgeon['phone']}<br>
                Website: <a href="{surgeon['website']}" target="_blank">{surgeon['website']}</a>
            """
            
            # Add marker to cluster
            folium.Marker(
                location=[coords['lat'], coords['lng']],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color='blue', icon='plus')
            ).add_to(marker_cluster)
            
        except Exception as e:
            print(f"Error adding marker for {surgeon['name']}: {str(e)}")
    
    # Add the marker cluster to the map
    marker_cluster.add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save map to HTML file
    map_file = 'all_surgeons_map.html'
    m.save(map_file)
    
    # Open in browser
    abs_path = 'file://' + os.path.abspath(map_file)
    print(f"Map saved to: {abs_path}")
    webbrowser.open(abs_path)

if __name__ == "__main__":
    print("Creating world map of all surgeons...")
    create_world_surgeon_map()
    print("Done! Map should open in your default browser.") 