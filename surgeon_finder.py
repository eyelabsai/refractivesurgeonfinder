import googlemaps
from typing import Dict, List

class SurgeonFinder:
    def __init__(self, api_key: str):
        self.gmaps = googlemaps.Client(key=api_key)
    
    def find_practice_address(self, state: str, doctor_name: str, practice_name: str) -> Dict:
        """
        Search for a practice's full details using Google Places API
        """
        # Construct search query
        search_query = f"{practice_name} {doctor_name} {state}"
        
        try:
            # Search for the business
            places_result = self.gmaps.places(search_query)
            
            if places_result['results']:
                place = places_result['results'][0]
                # Get detailed information
                place_details = self.gmaps.place(place['place_id'])['result']
                
                return {
                    'name': doctor_name,
                    'practice_name': practice_name,
                    'address': place_details.get('formatted_address'),
                    'phone': place_details.get('formatted_phone_number'),
                    'website': place_details.get('website'),
                    'zip_code': self._extract_zip_code(place_details.get('formatted_address')),
                    'coordinates': place_details.get('geometry', {}).get('location')
                }
            
            return None
            
        except Exception as e:
            print(f"Error finding address for {doctor_name}: {str(e)}")
            return None
    
    def _extract_zip_code(self, address: str) -> str:
        """Extract ZIP code from address string"""
        if not address:
            return None
        # Basic ZIP code extraction - you might want to make this more robust
        parts = address.split()
        for part in parts:
            if part.isdigit() and len(part) == 5:
                return part
        return None 