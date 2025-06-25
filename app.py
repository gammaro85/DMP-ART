# app.py - Enhanced Flask application with About page
import os
import json
import time
import threading
import zipfile
from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from utils.extractor import DMPExtractor

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}
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
    "data_format": "Please specify all data formats (CSV, JSON, TIFF, etc.) with examples.",
    "data_volume": "Estimate the total volume of data expected (in GB/TB).",
    "metadata": "Consider using established metadata standards like DataCite in your field.",
    "quality": "Implement validation procedures to ensure data quality and reproducibility.",
    "storage": "Specify the exact storage solutions and backup procedures you'll be using.",
    "backup": "Your backup strategy should include off-site copies and regular testing.",
    "security": "Detail encryption methods and access controls for sensitive data.",
    "personal_data": "Clarify compliance with GDPR and data minimization strategies.",
    "license": "Specify the exact licensing arrangements (e.g., Creative Commons) for your data.",
    "sharing": "Provide specific milestones and timelines for data publication.",
    "preservation": "Detail your long-term preservation strategy and repository selection criteria.",
    "tools": "List all required software tools with specific versions and accessibility.",
    "identifier": "Explain how and when DOIs will be assigned to datasets.",
    "responsibility": "Designate specific roles and responsibilities for data management tasks.",
    "resources": "Budget for dedicated staff time and resources for data management activities.",
    "table_extracted": "This content was extracted from a table structure - please verify accuracy.",
    "formatting_preserved": "Original formatting (bold/underlined) has been preserved where possible.",
    "simulation_data": "For simulation data, ensure reproducibility by documenting all parameters and software versions."
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def validate_docx_file(file_path):
    """Enhanced DOCX file validation"""
    try:
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        if not file_path.lower().endswith('.docx'):
            return False, "File is not a DOCX file"
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, "File is empty"
        
        if file_size > 16 * 1024 * 1024:  # 16MB limit
            return False, "File is too large (max 16MB)"
        
        # Check if it's a valid ZIP file (DOCX is ZIP-based)
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                required_files = ['word/document.xml', '[Content_Types].xml']
                
                for required_file in required_files:
                    if required_file not in file_list:
                        return False, f"Invalid DOCX structure: missing {required_file}"
                        
        except zipfile.BadZipFile:
            return False, "File is not a valid ZIP archive"
        except Exception as e:
            return False, f"ZIP validation error: {str(e)}"
        
        # Try to load with python-docx
        try:
            from docx import Document
            doc = Document(file_path)
            paragraph_count = len(doc.paragraphs)
            table_count = len(doc.tables)
            
            # Check for minimum content
            has_content = any(p.text.strip() for p in doc.paragraphs) or table_count > 0
            
            if not has_content:
                return False, "Document appears to be empty or contains no readable content"
                
        except Exception as e:
            return False, f"Document processing error: {str(e)}"
        
        return True, "File is valid"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def validate_pdf_file(file_path):
    """Enhanced PDF file validation"""
    try:
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        if not file_path.lower().endswith('.pdf'):
            return False, "File is not a PDF file"
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, "File is empty"
        
        if file_size > 16 * 1024 * 1024:  # 16MB limit
            return False, "File is too large (max 16MB)"
        
        # Try to read with PyPDF2
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                page_count = len(reader.pages)
                
                if page_count == 0:
                    return False, "PDF contains no pages"
                
                # Try to extract text from first page
                try:
                    first_page_text = reader.pages[0].extract_text()
                    if not first_page_text.strip():
                        return False, "PDF appears to contain no readable text"
                except Exception:
                    return False, "Cannot extract text from PDF"
                    
        except Exception as e:
            return False, f"PDF processing error: {str(e)}"
        
        return True, "File is valid"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/documentation')
def documentation():
    """Documentation page with features and technical information"""
    return render_template('documentation.html')

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
     
        
            # Enhanced file validation based on type
            if filename.lower().endswith('.docx'):
                is_valid, validation_message = validate_docx_file(file_path)
                if not is_valid:
                    try:
                        os.remove(file_path)
                    except:
                        pass
                    return jsonify({
                        'success': False,
                        'message': f'DOCX validation failed: {validation_message}'
                    })
            elif filename.lower().endswith('.pdf'):
                is_valid, validation_message = validate_pdf_file(file_path)
                if not is_valid:
                    try:
                        os.remove(file_path)
                    except:
                        pass
                    return jsonify({
                        'success': False,
                        'message': f'PDF validation failed: {validation_message}'
                    })
            
            # Process the file
            extractor = DMPExtractor()
            result = extractor.process_file(file_path, app.config['OUTPUT_FOLDER'])
            
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
                    'redirect': url_for('review_dmp', filename=result['filename'], cache_id=cache_id),
                    'message': result.get('message', 'File processed successfully')
                })
            else:
                return jsonify(result)
                
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Error processing file: {str(e)}")
            print(traceback_str)
            
            # Clean up uploaded file in case of error
            try:
                if 'file_path' in locals():
                    os.remove(file_path)
            except:
                pass
                
            return jsonify({
                'success': False,
                'message': f'Error processing file: {str(e)}'
            })
    
    return jsonify({
        'success': False,
        'message': 'Invalid file format. Only PDF and DOCX files are allowed.'
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
    extraction_info = {}
    
    if cache_id:
        cache_path = os.path.join(app.config['OUTPUT_FOLDER'], f"cache_{cache_id}.json")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    extracted_content = cache_data
                    
                    # Add extraction info for display
                    extraction_info = {
                        'total_sections': len([k for k in extracted_content.keys() if k.startswith(('1.', '2.', '3.', '4.', '5.', '6.'))]),
                        'sections_with_content': len([k for k, v in extracted_content.items() if v.get('paragraphs') and len(v['paragraphs']) > 0]),
                        'extraction_method': 'Enhanced DOCX processing with table support' if filename.lower().endswith('.docx') else 'PDF text extraction'
                    }
                    
            except Exception as e:
                print(f"Error loading extracted content: {str(e)}")
    
    # Pass the templates, common comments, and extracted content to the template
    return render_template('review.html', 
                           filename=filename,
                           templates=DMP_TEMPLATES,
                           comments=COMMON_COMMENTS,
                           extracted_content=extracted_content,
                           extraction_info=extraction_info,
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

@app.route('/save_comments', methods=['POST'])
def save_comments():
    try:
        data = request.json
        global COMMON_COMMENTS
        
        # Update the comments with the new data
        COMMON_COMMENTS.update(data)
        
        return jsonify({
            'success': True,
            'message': 'Comments saved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving comments: {str(e)}'
        })

@app.route('/save_key_phrases', methods=['POST'])
def save_key_phrases():
    try:
        data = request.json
        
        # Save key phrases to a file (in a real application, you'd save to database)
        key_phrases_path = os.path.join('config', 'key_phrases.json')
        os.makedirs(os.path.dirname(key_phrases_path), exist_ok=True)
        
        with open(key_phrases_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Key phrases saved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving key phrases: {str(e)}'
        })

@app.route('/save_dmp_structure', methods=['POST'])
def save_dmp_structure():
    try:
        data = request.json
        
        # Save DMP structure to a file
        structure_path = os.path.join('config', 'dmp_structure.json')
        os.makedirs(os.path.dirname(structure_path), exist_ok=True)
        
        with open(structure_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'DMP structure saved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving DMP structure: {str(e)}'
        })

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/template_editor')
def template_editor():
    # Load configuration files
    try:
        # Load key phrases
        key_phrases_path = os.path.join('config', 'key_phrases.json')
        if os.path.exists(key_phrases_path):
            with open(key_phrases_path, 'r', encoding='utf-8') as f:
                key_phrases = json.load(f)
        else:
            # Default key phrases from extractor
            extractor = DMPExtractor()
            key_phrases = extractor.get_key_phrases()
        
        # Load DMP structure
        structure_path = os.path.join('config', 'dmp_structure.json')
        if os.path.exists(structure_path):
            with open(structure_path, 'r', encoding='utf-8') as f:
                dmp_structure = json.load(f)
        else:
            # Default structure from extractor
            extractor = DMPExtractor()
            dmp_structure = extractor.dmp_structure
            
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        # Use defaults
        extractor = DMPExtractor()
        key_phrases = extractor.get_key_phrases()
        dmp_structure = extractor.dmp_structure
    
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
    
    return render_template('template_editor.html', 
                           templates_by_section=templates_by_section,
                           comments=COMMON_COMMENTS,
                           key_phrases=key_phrases,
                           dmp_structure=dmp_structure)

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

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'output_folder': app.config['OUTPUT_FOLDER'],
        'allowed_extensions': list(app.config['ALLOWED_EXTENSIONS']),
        'max_content_length': app.config['MAX_CONTENT_LENGTH']
    })

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'success': False,
        'message': 'File too large. Maximum size is 16MB.'
    }), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'message': 'Resource not found.'
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'success': False,
        'message': 'Internal server error. Please try again.'
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)