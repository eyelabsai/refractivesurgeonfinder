from surgeon_finder import SurgeonFinder
import csv
import time

def parse_surgeon_line(line: str) -> tuple:
    """Parse a line of surgeon data"""
    parts = line.split('\\')
    location, doctor = parts[0].split('–')
    practice = parts[1].strip() if len(parts) > 1 else None
    return location.strip(), doctor.strip(), practice

def main():
    api_key = 'AIzaSyAyOOjhdoifte9aAgC3ECOVUT8cXD8tMDY'
    finder = SurgeonFinder(api_key)
    
    # Store processed results
    results = []
    errors = []
    count = 0
    
    print("Starting to process surgeons...")
    
    with open('surgeons.txt', 'r') as f:
        current_state = None
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            if '–' not in line:
                current_state = line
                print(f"\nProcessing {current_state}")
                continue
                
            try:
                location, doctor, practice = parse_surgeon_line(line)
                print(f"Looking up: {doctor} at {practice}")
                
                # Find full address and details
                details = finder.find_practice_address(current_state, doctor, practice)
                if details:
                    results.append(details)
                    count += 1
                    print(f"✓ Found address for {doctor}")
                else:
                    errors.append(f"Could not find address for {doctor} at {practice}")
                    print(f"✗ No address found for {doctor}")
                
                # Add a small delay to avoid hitting API rate limits
                time.sleep(0.5)
                
            except Exception as e:
                errors.append(f"Error processing {line}: {str(e)}")
                print(f"✗ Error processing entry: {str(e)}")
    
    # Save results to CSV
    with open('surgeons_with_addresses.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'practice_name', 'address', 'phone', 'website', 'zip_code', 'coordinates'])
        writer.writeheader()
        writer.writerows(results)
    
    # Save errors to a separate file
    with open('processing_errors.txt', 'w') as f:
        f.write('\n'.join(errors))
    
    print(f"\nProcessing complete!")
    print(f"Successfully processed {count} surgeons")
    print(f"Encountered {len(errors)} errors")
    print("Results saved to surgeons_with_addresses.csv")
    print("Errors saved to processing_errors.txt")

if __name__ == "__main__":
    main() 