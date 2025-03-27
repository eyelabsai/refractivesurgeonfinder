# Save this as fix_coordinates.py

# Open the input file and read its content
with open('surgeons-data.js', 'r') as file:
    content = file.read()

# Perform the 3 replacements
content = content.replace('"coordinates": "{\\'lat\':', '"coordinates": {"lat":')
content = content.replace(', \'lng\':', ', "lng":')
content = content.replace('}"', '}')

# Write the modified content to a new file
with open('surgeons-data-fixed.js', 'w') as file:
    file.write(content)

print("Replacements completed. Output saved to surgeons-data-fixed.js")