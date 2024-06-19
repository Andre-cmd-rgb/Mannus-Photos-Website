import os

image_folder = 'images/thumbs'
output_file = 'index.html'

# Get list of image filenames
images = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]

# Generate the image list JavaScript code
image_list_code = 'const images = [\n' + ',\n'.join(f'    "{image}"' for image in images) + '\n];\n'

# Read the index.html file
with open(output_file, 'r') as file:
    content = file.read()

# Replace the placeholder with the generated image list code
content = content.replace('// IMAGE_LIST_PLACEHOLDER', image_list_code)

# Write the updated content back to the index.html file
with open(output_file, 'w') as file:
    file.write(content)

print('Image list generated and inserted into index.html')
