"""
Building the Flask server for my image processing app

Flask: The main framework to build the web app.
request: Handles incoming HTTP requests, such as file uploads.
jsonify: Converts Python objects (e.g., dictionaries) into JSON format for API responses.
render_template: Renders HTML templates for the frontend.

Pillow (PIL): A library for image processing, used to manipulate images (e.g., resizing, filters).

os: Helps with file and directory operations, such as creating folders or saving files.
io: Provides tools for handling in-memory file-like objects.
"""
from flask import Flask, request, jsonify, render_template, send_from_directory
from PIL import Image
import os
import io


app = Flask(__name__) # initialize Flask application object. It sets up the web server and handles requests.

#===================================Configure uploads folder=====================================================
upload_dir = 'uploads' # Name of directory where uploaded images will be stored
os.makedirs(upload_dir, exist_ok=True) # Creates the uploads directory if it doesn’t already exist.
app.config['upload_folder'] = upload_dir # Configures Flask to use upload_dir for saving files

#=========================================Define Routes==========================================================
# Homepage 
@app.route('/') # Defines a route for the homepage (/). When a user visits the base URL, this function runs.
# Renders the index.html file from the templates dir as the homepage.
def index():
    return render_template('index.html') 


# Defines a route for image uploads and processing
# The route accepts only POST requests, typically used for sending data like files.
@app.route('/process', methods=['POST'])
# Function to handle uploaded files, process images, and send responses.
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['image']
    operation = request.form.get('operation')  # Get the selected processing option

    try:
        # Open the image
        image = Image.open(file)
        filename = operation + '_' + str(file).split()[1][1:-1]

        # Perform the selected operation
        if operation == 'grayscale':
            processed_image = image.convert('L')  # Convert to grayscale
        elif operation == 'resize':
            # Get user-defined dimensions
            width = request.form.get('width')
            height = request.form.get('height')

            # Validate dimensions
            if not width or not height or not width.isdigit() or not height.isdigit():
                return jsonify({'error': 'Invalid width or height'}), 400

            width, height = int(width), int(height)
            processed_image = image.resize((width, height))  # Resize to user-defined dimensions
        elif operation == 'blur':
            from PIL import ImageFilter
            processed_image = image.filter(ImageFilter.BLUR)  # Apply blur
        elif operation == 'edge':
            from PIL import ImageFilter
            processed_image = image.filter(ImageFilter.FIND_EDGES)  # Edge detection
        else:
            return jsonify({'error': 'Invalid operation selected'}), 400

        # Save the processed image
        save_path = os.path.join(app.config['upload_folder'], filename)
        processed_image.save(save_path)

        return jsonify({
            'message': 'Image processed successfully!',
            'path': f'/uploads/{os.path.basename(save_path)}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Adds a new route to serve processed images:
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['upload_folder'], filename)

if __name__ == '__main__':
    app.run(debug=True)