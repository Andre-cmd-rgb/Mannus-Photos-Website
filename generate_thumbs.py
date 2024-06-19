from PIL import Image
import os

# Function to create thumbnails
def create_thumbnails(input_folder, output_folder, thumbnail_size=(200, 200)):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # List all files in the input folder
    files = os.listdir(input_folder)
    
    # Filter image files
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    
    for image_file in image_files:
        # Open image using Pillow
        with Image.open(os.path.join(input_folder, image_file)) as img:
            # Create thumbnail
            img.thumbnail(thumbnail_size)
            
            # Save thumbnail to output folder
            thumbnail_path = os.path.join(output_folder, image_file)
            img.save(thumbnail_path)
            
            print(f'Thumbnail created: {thumbnail_path}')

# Specify input and output folders
input_folder = 'images/full'  # Path to your original images folder
output_folder = 'images/thumbs'  # Path to where thumbnails will be saved

# Specify the size of the thumbnails (width, height) in pixels
thumbnail_size = (200, 200)

# Call function to create thumbnails
create_thumbnails(input_folder, output_folder, thumbnail_size)
