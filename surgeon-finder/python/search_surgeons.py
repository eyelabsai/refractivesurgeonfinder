import sys
import json
from your_existing_code import SurgeonFinder

def main():
    if len(sys.argv) != 3:
        print(json.dumps({
            'error': 'Invalid arguments',
            'results': [],
            'map_html': ''
        }))
        return

    zip_code = sys.argv[1]
    radius = float(sys.argv[2])

    finder = SurgeonFinder()
    results = finder.find_nearby_surgeons(zip_code, radius)
    map_html = finder.create_search_map(zip_code, results, radius)

    print(json.dumps({
        'results': results,
        'map_html': map_html
    }))

if __name__ == '__main__':
    main() 