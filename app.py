# app.py
import os
import json
import time
import threading
from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from utils.extractor import DMPExtractor
from utils.templates_manager import TemplatesManager

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Initialize templates manager
templates_manager = TemplatesManager()

# Common feedback comments that can be inserted
COMMON_COMMENTS = {
    "methodology": "The methodology needs more detail on how data will be collected.",
    "data_format": "Please specify all data formats (CSV, JSON, etc.) with examples.",
    "data_volume": "Estimate the total volume of data expected (in GB/TB).",
    "metadata": "Consider using established metadata standards in your field.",
    "quality": "Implement validation procedures to ensure data quality.",
    "storage": "Specify the exact storage solutions you'll be using.",
    "backup": "Your backup strategy should include off-site copies.",
    "security": "Detail encryption methods and access controls for sensitive data.",
    "personal_data": "Clarify compliance with GDPR and data minimization strategies.",
    "license": "Specify the exact licensing arrangements for your data.",
    "sharing": "Provide specific milestones for data publication.",
    "preservation": "Detail your long-term preservation strategy and repository selection.",
    "tools": "List all required software tools with specific versions.",
    "identifier": "Explain how and when DOIs will be assigned to datasets.",
    "responsibility": "Designate specific roles and responsibilities for data management.",
    "resources": "Budget for dedicated staff time for data management."
}

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
            
            if result['success']:
                # Redirect to the review page with cache ID
                cache_id = result.get('cache_id', '')
                return jsonify({
                    'success': True,
                    'redirect': url_for('review_dmp', filename=result['filename'], cache_id=cache_id)
                })
            else:
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

@app.route('/review/<filename>')
def review_dmp(filename):
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    
    # Get cache_id from request
    cache_id = request.args.get('cache_id', '')
    
    # Load extracted content if available
    extracted_content = {}
    if cache_id:
        cache_path = os.path.join(app.config['OUTPUT_FOLDER'], f"cache_{cache_id}.json")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    extracted_content = json.load(f)
            except Exception as e:
                print(f"Error loading extracted content: {str(e)}")
    
    # Get templates from the template manager
    templates = templates_manager.get_templates()
    
    # Pass the templates, common comments, and extracted content to the template
    return render_template('review.html', 
                           filename=filename,
                           templates=templates,
                           comments=COMMON_COMMENTS,
                           extracted_content=extracted_content,
                           cache_id=cache_id)

@app.route('/save_templates', methods=['POST'])
def save_templates():
    try:
        data = request.json
        
        # Update the templates using the template manager
        success = templates_manager.save_templates(data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Templates saved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error saving templates'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving templates: {str(e)}'
        })

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/template_editor')
def template_editor():
    # Get templates from the template manager
    templates = templates_manager.get_templates()
    
    # Organize templates by section for better display
    templates_by_section = {
        "1. Data description and collection or re-use of existing data": {
            k: v for k, v in templates.items() if k.startswith("1.")
        },
        "2. Documentation and data quality": {
            k: v for k, v in templates.items() if k.startswith("2.")
        },
        "3. Storage and backup during the research process": {
            k: v for k, v in templates.items() if k.startswith("3.")
        },
        "4. Legal requirements, codes of conduct": {
            k: v for k, v in templates.items() if k.startswith("4.")
        },
        "5. Data sharing and long-term preservation": {
            k: v for k, v in templates.items() if k.startswith("5.")
        },
        "6. Data management responsibilities and resources": {
            k: v for k, v in templates.items() if k.startswith("6.")
        }
    }
    
    return render_template('template_editor.html', templates_by_section=templates_by_section)

@app.route('/save_feedback', methods=['POST'])
def save_feedback():
    try:
        data = request.json
        
        # Get filename and feedback text
        filename = data.get('filename', '')
        feedback = data.get('feedback', '')
        
        if not filename or not feedback:
            return jsonify({
                'success': False,
                'message': 'Missing filename or feedback text'
            })
        
        # Save feedback to a file
        feedback_filename = f"feedback_{os.path.splitext(filename)[0]}.txt"
        feedback_path = os.path.join(app.config['OUTPUT_FOLDER'], feedback_filename)
        
        with open(feedback_path, 'w', encoding='utf-8') as f:
            f.write(feedback)
        
        return jsonify({
            'success': True,
            'filename': feedback_filename,
            'path': feedback_path,
            'message': 'Feedback saved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving feedback: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True)