import os
import time
import threading
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from utils.extractor import DMPExtractor

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'message': 'No file part'
        })
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'message': 'No selected file'
        })
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Process the PDF
            extractor = DMPExtractor()
            result = extractor.process_pdf(file_path, app.config['OUTPUT_FOLDER'])
            
            # Clean up the uploaded file
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Warning: Could not remove uploaded file: {str(e)}")
            
            return jsonify(result)
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Error processing file: {str(e)}")
            print(traceback_str)
            return jsonify({
                'success': False,
                'message': f'Error processing file: {str(e)}'
            })
    
    return jsonify({
        'success': False,
        'message': 'Invalid file format. Only PDF files are allowed.'
    })

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if not os.path.exists(file_path):
            return "File not found", 404
        
        return send_file(
            file_path,
            as_attachment=True
        )
    except Exception as e:
        return f"Error downloading file: {str(e)}", 500

@app.route('/results')
def results():
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True)