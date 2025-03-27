import pandas as pd
import json

def convert_csv_to_js():
    # Read the CSV file
    df = pd.read_csv('surgeons_with_addresses.csv')
    
    # Convert to list of dictionaries
    surgeons = df.to_dict('records')
    
    # Create JavaScript file content
    js_content = f"const surgeonsData = {json.dumps(surgeons, indent=2)};"
    
    # Write to file
    with open('js/surgeons-data.js', 'w') as f:
        f.write(js_content)

if __name__ == '__main__':
    convert_csv_to_js() 