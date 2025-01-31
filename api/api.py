from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
from sourcing.functions.wmu_functions import load_wmu_data
import json

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'])

# Make sure this folder exists or create it
UPLOAD_FOLDER = 'sourcing/sources'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:  # Check if file is part of the request
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']  # Retrieve the file from the request

    if file.filename == '':  # If no file is selected
        return jsonify({'error': 'No selected file'}), 400

    file_name = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)

    try:
        # Save the file as a binary file
        file.save(file_path)
        return jsonify({'message': f'File {file_name} uploaded successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process-files', methods=['POST'])
def process_files():
    # only run when user clicks a button that says 'done uploading all files'
    source_path = 'sourcing/sources'
    pe1, pe2, mna, ipo, mgmt = load_wmu_data(source_path)

    return jsonify({'message': 'Files processed successfully!'}), 200


def save_config(config_data, CONFIG_FILE='./sourcing/sources/config/config.json'):
    """Save the configuration to a file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
        return jsonify({'message': 'Config file saved successfully!'}), 200
    except Exception as e:
        print("Error writing config file:", str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/save-config', methods=['POST'])
def save_config_route():
    config_data = request.get_json()

    if not config_data:
        return jsonify({'error': 'No configuration data provided'}), 400
    
    return save_config(config_data)

if __name__ == '__main__':
    app.run(debug=True)