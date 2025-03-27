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
    
    def get_coordinates_from_zip(self, zip_code, country=None):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                query = zip_code
                if country:
                    query = f"{zip_code}, {country}"
                location = self.geolocator.geocode(query, exactly_one=True)
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

    def get_coordinates_from_city(self, city, state=None, country=None):
        try:
            query = city
            if state and country:
                query = f"{city}, {state}, {country}"
            elif state:
                query = f"{city}, {state}"
            elif country:
                query = f"{city}, {country}"
                
            location = self.geolocator.geocode(query, exactly_one=True)
            if location:
                return (location.latitude, location.longitude)
        except Exception as e:
            print(f"Error finding coordinates for {query}: {str(e)}")
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

    def find_nearby_surgeons(self, zip_code, radius_miles=50, country=None):
        search_coords = self.get_coordinates_from_zip(zip_code, country)
        return self.find_nearby_surgeons_by_location(search_coords, radius_miles)

    def find_nearby_surgeons_by_city(self, city, state, radius_miles=50, country=None):
        search_coords = None
        try:
            # If city is provided, search by city and state
            if city:
                search_coords = self.get_coordinates_from_city(city, state, country)
            # If only state is provided, use state center
            elif state:
                # Handle international state searches properly
                query = state
                if country:
                    query = f"{state}, {country}"
                else:
                    # Default to USA if no country provided but assume it could be any state globally
                    # This helps with US state searches like "Louisiana"
                    query = state
                
                print(f"Searching for state location: {query}")
                location = self.geolocator.geocode(query, exactly_one=True)
                if location:
                    print(f"Found coordinates for {query}: {location.latitude}, {location.longitude}")
                    search_coords = (location.latitude, location.longitude)
                    # For state-only searches, increase zoom level
                    radius_miles = max(radius_miles, 200)  # Minimum 200 mile radius for state searches
                else:
                    print(f"Could not find coordinates for state: {query}")
        except Exception as e:
            print(f"Error finding coordinates for state search: {str(e)}")
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
        name_query = name_query.lower().strip()
        matching_surgeons = []
        print(f"Searching for name: '{name_query}'")
        
        # Count total surgeons for debugging
        total_surgeons = len(self.df)
        print(f"Total surgeons in database: {total_surgeons}")
        
        for index, surgeon in self.df.iterrows():
            try:
                # Debug the raw name data
                raw_name = surgeon.get('name', '')
                print(f"Raw name data for index {index}: '{raw_name}'")
                
                # Handle NaN or None values
                if pd.isna(raw_name) or raw_name is None:
                    continue
                    
                surgeon_name = str(raw_name).lower().strip()
                
                # Also search in practice name for better matching
                practice_name = str(surgeon.get('practice_name', '')).lower().strip()
                
                # Try different search approaches
                if (name_query in surgeon_name or 
                    surgeon_name.startswith(name_query) or 
                    name_query in practice_name):
                    
                    print(f"MATCH FOUND: {raw_name} | Practice: {surgeon.get('practice_name', '')}")
                    
                    # Get coordinates carefully
                    coords_str = surgeon.get('coordinates', '')
                    if pd.isna(coords_str) or not coords_str:
                        print(f"Warning: No coordinates for surgeon {raw_name}")
                        coords = {"lat": 0, "lng": 0}
                    else:
                        try:
                            coords = json.loads(str(coords_str).replace("'", '"'))
                        except:
                            print(f"Error parsing coordinates: {coords_str}")
                            coords = {"lat": 0, "lng": 0}
                    
                    matching_surgeons.append({
                        'name': raw_name,
                        'practice': surgeon.get('practice_name', ''),
                        'address': surgeon.get('address', ''),
                        'phone': surgeon.get('phone', ''),
                        'website': surgeon.get('website', ''),
                        'coordinates': (coords['lat'], coords['lng'])
                    })
            except Exception as e:
                print(f"Error processing surgeon at index {index}: {str(e)}")
                continue
                
        print(f"Total matches found: {len(matching_surgeons)}")
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
        country = request.form.get('country', '')
        
        if search_type == 'zip':
            zip_code = request.form.get('zip_code')
            # Pass the country if provided
            search_coords = surgeon_finder.get_coordinates_from_zip(zip_code, country if country else None)
            results = surgeon_finder.find_nearby_surgeons_by_location(search_coords, radius)
            
            map_html = None
            if search_coords:
                m = folium.Map(location=search_coords, zoom_start=10)
                folium.Marker(
                    search_coords,
                    popup=f"Search Center: {zip_code}",
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
            
            location_text = f"ZIP: {zip_code}" + (f", {country}" if country else "")
        else:
            city = request.form.get('city', '').strip()
            state = request.form.get('state', '').strip()
            
            # Find coordinates based on what's provided
            if city or state:
                if state and not city:
                    # State-only search
                    results = surgeon_finder.find_nearby_surgeons_by_city('', state, radius, country)
                    search_coords = None  # To avoid double search
                else:
                    # City + optional state search
                    search_coords = surgeon_finder.get_coordinates_from_city(city, state, country)
                    results = surgeon_finder.find_nearby_surgeons_by_location(search_coords, radius)
            else:
                search_coords = None
                results = []
            
            # Create the map
            map_html = None
            if search_coords or (state and not city and results):
                # If we only searched by state, we need to get coordinates for the map center
                if state and not city and not search_coords and results:
                    query = state
                    if country:
                        query = f"{state}, {country}"
                    location = surgeon_finder.geolocator.geocode(query, exactly_one=True)
                    if location:
                        search_coords = (location.latitude, location.longitude)
                
                if search_coords:
                    m = folium.Map(location=search_coords, zoom_start=6 if not city else 10)
                    
                    location_display = []
                    if city:
                        location_display.append(city)
                    if state:
                        location_display.append(state)
                    if country:
                        location_display.append(country)
                    
                    location_str = ", ".join(location_display)
                    
                    folium.Marker(
                        search_coords,
                        popup=f"Search Center: {location_str}",
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
                
            location_parts = []
            if city:
                location_parts.append(city)
            if state:
                location_parts.append(state)
            if country:
                location_parts.append(country)
            
            location_text = ", ".join(location_parts)
    
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
    # Use environment variable for port if available (for deployment)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

# Add this line to export the app for Vercel serverless function
app = app 