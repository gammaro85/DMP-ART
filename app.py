# app.py
import os
import json
import time
import threading
from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
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

# DMP question templates with default text
DMP_TEMPLATES = {
    "1.1": {
        "question": "How will new data be collected or produced and/or how will existing data be re-used?",
        "template": "The data collection methodology needs more detail. Please specify the exact sources and collection methods."
    },
    "1.2": {
        "question": "What data (for example the types, formats, and volumes) will be collected or produced?",
        "template": "Please provide more specific information about data formats and expected volumes."
    },
    "2.1": {
        "question": "What metadata and documentation will accompany data?",
        "template": "The metadata standards should be clearly specified. Consider using established standards in your field."
    },
    "2.2": {
        "question": "What data quality control measures will be used?",
        "template": "More rigorous quality control measures should be implemented. Consider validation procedures."
    },
    "3.1": {
        "question": "How will data and metadata be stored and backed up during the research process?",
        "template": "Your backup strategy needs improvement. Consider redundant storage solutions."
    },
    "3.2": {
        "question": "How will data security and protection of sensitive data be taken care of during the research?",
        "template": "The security measures seem inadequate. Please detail encryption methods and access controls."
    },
    "4.1": {
        "question": "If personal data are processed, how will compliance with legislation be ensured?",
        "template": "Your GDPR compliance plan needs more detail. Specify consent procedures and data minimization strategies."
    },
    "4.2": {
        "question": "How will other legal issues, such as intellectual property rights and ownership, be managed?",
        "template": "Intellectual property considerations are unclear. Please specify licensing arrangements."
    },
    "5.1": {
        "question": "How and when will data be shared? Are there possible restrictions?",
        "template": "Data sharing timeline is vague. Please provide specific milestones for data publication."
    },
    "5.2": {
        "question": "How will data for preservation be selected, and where will data be preserved long-term?",
        "template": "Long-term preservation strategy needs more detail. Specify repository selection criteria."
    },
    "5.3": {
        "question": "What methods or software tools will be needed to access and use the data?",
        "template": "Software documentation is insufficient. Please list all required tools and versions."
    },
    "5.4": {
        "question": "How will the application of a unique and persistent identifier to each data set be ensured?",
        "template": "Your DOI implementation plan lacks detail. Specify exactly how and when identifiers will be assigned."
    },
    "6.1": {
        "question": "Who will be responsible for data management?",
        "template": "Data stewardship responsibilities are unclear. Please designate specific roles and responsibilities."
    },
    "6.2": {
        "question": "What resources will be dedicated to data management and ensuring the data will be FAIR?",
        "template": "Resource allocation for data management seems insufficient. Consider budgeting for dedicated staff time."
    }
}

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
    
    # Pass the templates, common comments, and extracted content to the template
    return render_template('review.html', 
                           filename=filename,
                           templates=DMP_TEMPLATES,
                           comments=COMMON_COMMENTS,
                           extracted_content=extracted_content,
                           cache_id=cache_id)

@app.route('/save_templates', methods=['POST'])
def save_templates():
    try:
        data = request.json
        global DMP_TEMPLATES
        
        # Update the templates with the new data
        for key, value in data.items():
            if key in DMP_TEMPLATES:
                DMP_TEMPLATES[key]['template'] = value
        
        return jsonify({
            'success': True,
            'message': 'Templates saved successfully'
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
    # Organize templates by section for better display
    templates_by_section = {
        "1. Data description and collection or re-use of existing data": {
            k: v for k, v in DMP_TEMPLATES.items() if k.startswith("1.")
        },
        "2. Documentation and data quality": {
            k: v for k, v in DMP_TEMPLATES.items() if k.startswith("2.")
        },
        "3. Storage and backup during the research process": {
            k: v for k, v in DMP_TEMPLATES.items() if k.startswith("3.")
        },
        "4. Legal requirements, codes of conduct": {
            k: v for k, v in DMP_TEMPLATES.items() if k.startswith("4.")
        },
        "5. Data sharing and long-term preservation": {
            k: v for k, v in DMP_TEMPLATES.items() if k.startswith("5.")
        },
        "6. Data management responsibilities and resources": {
            k: v for k, v in DMP_TEMPLATES.items() if k.startswith("6.")
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