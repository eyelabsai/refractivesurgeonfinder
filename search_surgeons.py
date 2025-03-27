import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import json
import folium
from folium import plugins
import webbrowser
import os

class SurgeonSearch:
    def __init__(self):
        # Read the CSV file
        self.df = pd.read_csv('surgeons_with_addresses.csv')
        self.geolocator = Nominatim(user_agent="surgeon_finder")
        
    def get_coordinates_from_zip(self, zip_code):
        """Get latitude and longitude from ZIP code"""
        try:
            location = self.geolocator.geocode(f"{zip_code}, USA")
            if location:
                return (location.latitude, location.longitude)
        except Exception as e:
            print(f"Error finding coordinates for ZIP code {zip_code}: {str(e)}")
        return None
        
    def find_nearby_surgeons(self, zip_code, radius_miles=50):
        """Find surgeons within specified radius of ZIP code"""
        # Get coordinates for the search ZIP code
        search_coords = self.get_coordinates_from_zip(zip_code)
        if not search_coords:
            return []
            
        nearby_surgeons = []
        
        for _, surgeon in self.df.iterrows():
            # Get surgeon coordinates from the 'coordinates' field
            try:
                coords = json.loads(surgeon['coordinates'].replace("'", '"'))
                surgeon_coords = (coords['lat'], coords['lng'])
                
                # Calculate distance
                distance = geodesic(search_coords, surgeon_coords).miles
                
                if distance <= radius_miles:
                    nearby_surgeons.append({
                        'name': surgeon['name'],
                        'practice': surgeon['practice_name'],
                        'address': surgeon['address'],
                        'phone': surgeon['phone'],
                        'website': surgeon['website'],
                        'distance': round(distance, 1),
                        'coordinates': surgeon_coords
                    })
            except:
                continue
                
        # Sort by distance
        return sorted(nearby_surgeons, key=lambda x: x['distance'])

    def create_map(self, zip_code, results, radius_miles):
        """Create an interactive map with the search results"""
        # Get coordinates for the search ZIP code
        center_coords = self.get_coordinates_from_zip(zip_code)
        
        if not center_coords or not results:
            return None
            
        # Create a map centered on the search location
        m = folium.Map(location=center_coords, zoom_start=10)
        
        # Add a marker for the search location
        folium.Marker(
            center_coords,
            popup=f"Search Center: {zip_code}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        # Add markers for each surgeon
        for surgeon in results:
            # Create popup content
            popup_html = f"""
                <b>{surgeon['name']}</b><br>
                Practice: {surgeon['practice']}<br>
                Address: {surgeon['address']}<br>
                Phone: {surgeon['phone']}<br>
                Website: <a href="{surgeon['website']}" target="_blank">{surgeon['website']}</a><br>
                Distance: {surgeon['distance']} miles
            """
            
            # Add marker
            folium.Marker(
                surgeon['coordinates'],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color='blue', icon='plus')
            ).add_to(m)
            
        # Add circle showing search radius
        folium.Circle(
            center_coords,
            radius=radius_miles * 1609.34,  # Convert miles to meters
            color='red',
            fill=True,
            opacity=0.2
        ).add_to(m)
        
        # Save map to HTML file
        map_file = 'surgeon_map.html'
        m.save(map_file)
        return map_file

def main():
    searcher = SurgeonSearch()
    
    while True:
        zip_code = input("\nEnter ZIP code to search (or 'quit' to exit): ")
        if zip_code.lower() == 'quit':
            break
            
        radius = input("Enter search radius in miles (default 50): ")
        radius_miles = float(radius) if radius.strip() else 50
        
        print(f"\nSearching for surgeons within {radius_miles} miles of {zip_code}...")
        results = searcher.find_nearby_surgeons(zip_code, radius_miles)
        
        if not results:
            print("No surgeons found in that area.")
            continue
            
        print(f"\nFound {len(results)} surgeons:")
        for i, surgeon in enumerate(results, 1):
            print(f"\n{i}. {surgeon['name']}")
            print(f"   Practice: {surgeon['practice']}")
            print(f"   Address: {surgeon['address']}")
            print(f"   Phone: {surgeon['phone']}")
            print(f"   Website: {surgeon['website']}")
            print(f"   Distance: {surgeon['distance']} miles")
        
        # Create and display map
        map_file = searcher.create_map(zip_code, results, radius_miles)
        if map_file:
            print(f"\nOpening map in your browser...")
            # Get absolute path to the file
            abs_path = 'file://' + os.path.abspath(map_file)
            print(f"Map saved to: {abs_path}")
            webbrowser.open(abs_path)

if __name__ == "__main__":
    main() 