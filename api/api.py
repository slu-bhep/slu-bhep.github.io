from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)

CORS(app, origins=['http://localhost:3000'])

@app.route('/upload', methods=['POST'])
def upload_file():
    file_data = request.get_json()

    if not file_data:
        return jsonify({'error': 'No file data received'}), 400
    
    file_name = file_data.get('name')
    file_content = file_data.get('content')

    if not file_name or not file_content:
        return jsonify({'error': 'Invalid file data'}), 400
    
    with open(f'sourcing/sources/{file_name}', 'w') as f:
        f.write(file_content)

    return jsonify({'message': f'File {file_name} uploaded successfully!'}), 200

if __name__ == '__main__':
    app.run(debug=True)