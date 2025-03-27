from flask import Flask, render_template, request, jsonify
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import json
import folium
from folium.plugins import MarkerCluster
import os
import time

app = Flask(__name__)

class SurgeonFinder:
    def __init__(self):
        # Read the CSV file once when initializing
        self.df = pd.read_csv('surgeons_with_addresses.csv')
        self.geolocator = Nominatim(user_agent="surgeon_finder", timeout=5)
    
    def get_coordinates_from_zip(self, zip_code):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                location = self.geolocator.geocode(f"{zip_code}, USA", exactly_one=True)
                if location:
                    return (location.latitude, location.longitude)
                time.sleep(1)  # Add a small delay between retries
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for ZIP code {zip_code}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retrying
                continue
        print(f"Failed to find coordinates for ZIP code {zip_code} after {max_retries} attempts")
        return None

    def get_coordinates_from_city(self, city, state):
        try:
            location = self.geolocator.geocode(f"{city}, {state}, USA", exactly_one=True)
            if location:
                return (location.latitude, location.longitude)
        except Exception as e:
            print(f"Error finding coordinates for {city}, {state}: {str(e)}")
        return None

    def find_nearby_surgeons_by_location(self, coords, radius_miles=50):
        if not coords:
            return []
            
        nearby_surgeons = []
        
        for _, surgeon in self.df.iterrows():
            try:
                coords_data = json.loads(surgeon['coordinates'].replace("'", '"'))
                surgeon_coords = (coords_data['lat'], coords_data['lng'])
                distance = geodesic(coords, surgeon_coords).miles
                
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
                
        return sorted(nearby_surgeons, key=lambda x: x['distance'])

    def find_nearby_surgeons(self, zip_code, radius_miles=50):
        search_coords = self.get_coordinates_from_zip(zip_code)
        return self.find_nearby_surgeons_by_location(search_coords, radius_miles)

    def find_nearby_surgeons_by_city(self, city, state, radius_miles=50):
        search_coords = None
        try:
            # If city is provided, search by city and state
            if city:
                search_coords = self.get_coordinates_from_city(city, state)
            # If only state is provided, use state center
            else:
                location = self.geolocator.geocode(f"{state}, USA", exactly_one=True)
                if location:
                    search_coords = (location.latitude, location.longitude)
                    # For state-only searches, increase zoom level
                    radius_miles = max(radius_miles, 200)  # Minimum 200 mile radius for state searches
        except Exception as e:
            print(f"Error finding coordinates: {str(e)}")
        return self.find_nearby_surgeons_by_location(search_coords, radius_miles)

    def create_search_map(self, zip_code, results, radius_miles):
        center_coords = self.get_coordinates_from_zip(zip_code)
        if not center_coords or not results:
            return None
            
        m = folium.Map(location=center_coords, zoom_start=10)
        
        # Add search center marker
        folium.Marker(
            center_coords,
            popup=f"Search Center: {zip_code}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        # Add surgeon markers
        for surgeon in results:
            popup_html = f"""
                <b>{surgeon['name']}</b><br>
                Practice: {surgeon['practice']}<br>
                Address: {surgeon['address']}<br>
                Phone: {surgeon['phone']}<br>
                Website: <a href="{surgeon['website']}" target="_blank">{surgeon['website']}</a><br>
                Distance: {surgeon['distance']} miles
            """
            
            folium.Marker(
                surgeon['coordinates'],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color='blue', icon='plus')
            ).add_to(m)
            
        # Add search radius circle
        folium.Circle(
            center_coords,
            radius=radius_miles * 1609.34,
            color='red',
            fill=True,
            opacity=0.2
        ).add_to(m)
        
        return m._repr_html_()

    def create_world_map(self):
        m = folium.Map(location=[20, 0], zoom_start=2)
        marker_cluster = MarkerCluster(name="Surgeons")
        
        for _, surgeon in self.df.iterrows():
            try:
                coords = eval(str(surgeon['coordinates']))
                popup_html = f"""
                    <b>{surgeon['name']}</b><br>
                    Practice: {surgeon['practice_name']}<br>
                    Address: {surgeon['address']}<br>
                    Phone: {surgeon['phone']}<br>
                    Website: <a href="{surgeon['website']}" target="_blank">{surgeon['website']}</a>
                """
                
                folium.Marker(
                    location=[coords['lat'], coords['lng']],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color='blue', icon='plus')
                ).add_to(marker_cluster)
                
            except Exception as e:
                print(f"Error adding marker for {surgeon['name']}: {str(e)}")
        
        marker_cluster.add_to(m)
        folium.LayerControl().add_to(m)
        
        return m._repr_html_()

    def find_surgeons_by_name(self, name_query):
        """Search surgeons by name keyword"""
        name_query = name_query.lower()
        matching_surgeons = []
        
        for _, surgeon in self.df.iterrows():
            try:
                if name_query in surgeon['name'].lower():
                    coords = json.loads(surgeon['coordinates'].replace("'", '"'))
                    matching_surgeons.append({
                        'name': surgeon['name'],
                        'practice': surgeon['practice_name'],
                        'address': surgeon['address'],
                        'phone': surgeon['phone'],
                        'website': surgeon['website'],
                        'coordinates': (coords['lat'], coords['lng'])
                    })
            except:
                continue
                
        return matching_surgeons

    def create_name_search_map(self, results):
        """Create a map for name search results"""
        if not results:
            return None
            
        # Find center point from all results
        lats = [r['coordinates'][0] for r in results]
        lngs = [r['coordinates'][1] for r in results]
        center_lat = sum(lats) / len(lats)
        center_lng = sum(lngs) / len(lngs)
            
        m = folium.Map(location=[center_lat, center_lng], zoom_start=4)
        
        # Add surgeon markers
        for surgeon in results:
            popup_html = f"""
                <b>{surgeon['name']}</b><br>
                Practice: {surgeon['practice']}<br>
                Address: {surgeon['address']}<br>
                Phone: {surgeon['phone']}<br>
                Website: <a href="{surgeon['website']}" target="_blank">{surgeon['website']}</a>
            """
            
            folium.Marker(
                surgeon['coordinates'],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color='blue', icon='plus')
            ).add_to(m)
            
        return m._repr_html_()

# Initialize the surgeon finder
surgeon_finder = SurgeonFinder()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_type = request.form.get('search_type', 'zip')
    
    if search_type == 'name':
        name_query = request.form.get('name_query')
        results = surgeon_finder.find_surgeons_by_name(name_query)
        map_html = surgeon_finder.create_name_search_map(results)
        location_text = f'Name: "{name_query}"'
        radius = None
    else:
        radius = float(request.form.get('radius', 50))
        if search_type == 'zip':
            zip_code = request.form.get('zip_code')
            results = surgeon_finder.find_nearby_surgeons(zip_code, radius)
            map_html = surgeon_finder.create_search_map(zip_code, results, radius)
            location_text = f"ZIP: {zip_code}"
        else:
            city = request.form.get('city', '').strip()
            state = request.form.get('state')
            results = surgeon_finder.find_nearby_surgeons_by_city(city, state, radius)
            search_coords = surgeon_finder.get_coordinates_from_city(city, state) if city else None
            if not search_coords:
                location = surgeon_finder.geolocator.geocode(f"{state}, USA", exactly_one=True)
                if location:
                    search_coords = (location.latitude, location.longitude)
            
            map_html = None
            if search_coords:
                m = folium.Map(location=search_coords, zoom_start=6 if not city else 10)
                folium.Marker(
                    search_coords,
                    popup=f"Search Center: {city + ', ' if city else ''}{state}",
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(m)
                
                for surgeon in results:
                    popup_html = f"""
                        <b>{surgeon['name']}</b><br>
                        Practice: {surgeon['practice']}<br>
                        Address: {surgeon['address']}<br>
                        Phone: {surgeon['phone']}<br>
                        Website: <a href="{surgeon['website']}" target="_blank">{surgeon['website']}</a><br>
                        Distance: {surgeon['distance']} miles
                    """
                    
                    folium.Marker(
                        surgeon['coordinates'],
                        popup=folium.Popup(popup_html, max_width=300),
                        icon=folium.Icon(color='blue', icon='plus')
                    ).add_to(m)
                    
                folium.Circle(
                    search_coords,
                    radius=radius * 1609.34,
                    color='red',
                    fill=True,
                    opacity=0.2
                ).add_to(m)
                
                map_html = m._repr_html_()
            location_text = f"{city + ', ' if city else ''}{state}"
    
    return render_template('results.html', 
                         results=results, 
                         map_html=map_html,
                         location=location_text,
                         radius=radius)

@app.route('/world-map')
def world_map():
    map_html = surgeon_finder.create_world_map()
    return render_template('world_map.html', map_html=map_html)

if __name__ == '__main__':
    app.run(debug=True) 