# app.py - Enhanced Flask application with About page
import os
import json
import time
import threading
import zipfile
from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from utils.extractor import DMPExtractor
# Comments are now managed through JSON files in config/ directory

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

# Template categories will be managed through template editor

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

@app.route('/test_categories_page')
def test_categories_page():
    """Test page for debugging category loading"""
    return render_template('test_categories.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'message': 'No file part'
        })
    
    file = request.files['file']
    
    if not file or not file.filename:
        return jsonify({
            'success': False,
            'message': 'No selected file'
        })
    
    file_path = None  # Ensure file_path is always defined
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename or "")
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
            # Fix: Ensure file_path is defined before attempting to remove
            try:
                if file_path is not None:
                    os.remove(file_path)
            except Exception:
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
    
    cache_id = request.args.get('cache_id', '')
    
    extracted_content = {}
    extraction_info = {}
    unconnected_text = []
    
    if cache_id:
        cache_path = os.path.join(app.config['OUTPUT_FOLDER'], f"cache_{cache_id}.json")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                    if cache_data is not None:
                        if "_unconnected_text" in cache_data:
                            unconnected_text = cache_data["_unconnected_text"]
                            del cache_data["_unconnected_text"]
                        extracted_content = cache_data
                        extraction_info = {
                            'total_sections': len([k for k in extracted_content.keys() if k.startswith(('1.', '2.', '3.', '4.', '5.', '6.'))]),
                            'sections_with_content': len([k for k, v in extracted_content.items() if v.get('paragraphs') and len(v['paragraphs']) > 0]),
                            'extraction_method': 'Enhanced DOCX processing with table support' if filename.lower().endswith('.docx') else 'PDF text extraction'
                        }
            except Exception as e:
                print(f"Error loading extracted content: {str(e)}")
    
    return render_template('review.html', 
                           filename=filename,
                           templates=DMP_TEMPLATES,
                           extracted_content=extracted_content,
                           extraction_info=extraction_info,
                           unconnected_text=unconnected_text,
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

# Removed /save_comments endpoint

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
    try:
        structure_path = os.path.join('config', 'dmp_structure.json')
        if os.path.exists(structure_path):
            with open(structure_path, 'r', encoding='utf-8') as f:
                dmp_structure = json.load(f)
        else:
            extractor = DMPExtractor()
            dmp_structure = extractor.dmp_structure
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        extractor = DMPExtractor()
        dmp_structure = extractor.dmp_structure
    
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
    
    # Removed comments=COMMON_COMMENTS
    return render_template('template_editor.html', 
                           templates=DMP_TEMPLATES,
                           templates_by_section=templates_by_section,
                           dmp_structure=dmp_structure)

@app.route('/save_feedback', methods=['POST'])
def save_feedback():
    try:
        data = request.json or {}
        
        filename = data.get('filename', '')
        feedback = data.get('feedback', '')
        
        if not filename or not feedback:
            return jsonify({
                'success': False,
                'message': 'Missing filename or feedback text'
            })
        
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

@app.route('/save_category', methods=['POST'])
def save_category():
    """Save category with its comments"""
    try:
        data = request.json or {}
        file = data.get('file')
        category_data = data.get('data', {})
        
        if not file:
            return jsonify({
                'success': False,
                'message': 'File name is required'
            })
        
        category_path = os.path.join('config', f'{file}.json')
        
        with open(category_path, 'w', encoding='utf-8') as f:
            json.dump(category_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': f'Category "{file}" saved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving category: {str(e)}'
        })

@app.route('/load_categories', methods=['GET'])
def load_categories():
    """Load all categories and their comments from individual JSON files"""
    try:
        config_dir = 'config'
        categories = {}

        if os.path.exists(config_dir):
            for filename in os.listdir(config_dir):
                if filename.endswith('.json') and filename not in ['dmp_structure.json', 'quick_comments.json']:
                    file_base = filename[:-5]
                    file_path = os.path.join(config_dir, filename)

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Ensure data is a dict before calling items
                            if isinstance(data, dict):
                                for key, value in data.items():
                                    if not key.startswith('_') and isinstance(value, dict):
                                        categories[key] = value
                                        break
                            else:
                                # If data is None or not a dict, skip
                                continue
                    except Exception as e:
                        print(f"Error loading category file {filename}: {str(e)}")
                        continue

        return jsonify({
            'success': True,
            'categories': categories
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading categories: {str(e)}'
        })

@app.route('/load_category_comments', methods=['GET'])
def load_category_comments():
    """Load category-specific comments for feedback sections"""
    try:
        category_comments_path = os.path.join('config', 'category_comments.json')
        
        if not os.path.exists(category_comments_path):
            return jsonify({
                'success': True,
                'category_comments': {}
            })
        
        with open(category_comments_path, 'r', encoding='utf-8') as f:
            category_comments = json.load(f)
            if category_comments is None:
                category_comments = {}
        
        return jsonify({
            'success': True,
            'category_comments': category_comments
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading category comments: {str(e)}'
        })

@app.route('/save_category_comments', methods=['POST'])
def save_category_comments():
    """Save category-specific comments for feedback sections"""
    try:
        data = request.json or {}
        category_comments = data.get('category_comments', {})
        
        category_comments_path = os.path.join('config', 'category_comments.json')
        os.makedirs(os.path.dirname(category_comments_path), exist_ok=True)
        
        with open(category_comments_path, 'w', encoding='utf-8') as f:
            json.dump(category_comments, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': 'Category comments saved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving category comments: {str(e)}'
        })

@app.route('/save_quick_comments', methods=['POST'])
def save_quick_comments():
    """Save quick comments"""
    try:
        data = request.json or {}
        quick_comments = data.get('quick_comments', [])
        
        quick_comments_path = os.path.join('config', 'quick_comments.json')
        
        with open(quick_comments_path, 'w', encoding='utf-8') as f:
            json.dump({
                "quick_comments": quick_comments
            }, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': 'Quick comments saved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving quick comments: {str(e)}'
        })

@app.route('/load_quick_comments', methods=['GET'])
def load_quick_comments():
    """Load quick comments"""
    try:
        quick_comments_path = os.path.join('config', 'quick_comments.json')
        
        if not os.path.exists(quick_comments_path):
            return jsonify({
                'success': True,
                'quick_comments': []
            })
        
        with open(quick_comments_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data is None:
                data = {}
        
        return jsonify({
            'success': True,
            'quick_comments': data.get('quick_comments', [])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading quick comments: {str(e)}'
        })

@app.route('/list_categories', methods=['GET'])
def list_categories():
    """List all available category files"""
    try:
        config_dir = 'config'
        categories = []
        
        if os.path.exists(config_dir):
            for filename in os.listdir(config_dir):
                if filename.endswith('.json') and filename not in ['dmp_structure.json', 'quick_comments.json']:
                    file_base = filename[:-5]
                    category_name = file_base.replace('_', ' ').title()
                    categories.append({
                        'file': file_base,
                        'name': category_name
                    })
        
        return jsonify({
            'success': True,
            'categories': categories
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error listing categories: {str(e)}'
        })

@app.route('/create_category', methods=['POST'])
def create_category():
    """Create a new category file"""
    try:
        data = request.json or {}
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({
                'success': False,
                'message': 'Category name is required'
            })
        
        file_name = name.lower().replace(' ', '_')
        category_path = os.path.join('config', f'{file_name}.json')
        
        if os.path.exists(category_path):
            return jsonify({
                'success': False,
                'message': 'Category with this name already exists'
            })
        
        category_data = {}
        
        with open(category_path, 'w', encoding='utf-8') as f:
            json.dump(category_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': f'Category "{name}" created successfully',
            'file': file_name
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating category: {str(e)}'
        })

@app.route('/delete_category', methods=['POST'])
def delete_category():
    """Delete a category file"""
    try:
        data = request.json or {}
        file = data.get('file', '').strip()
        
        if not file:
            return jsonify({
                'success': False,
                'message': 'File name is required'
            })
        
        category_path = os.path.join('config', f'{file}.json')
        
        if not os.path.exists(category_path):
            return jsonify({
                'success': False,
                'message': 'Category file does not exist'
            })
        
        os.remove(category_path)
        
        return jsonify({
            'success': True,
            'message': f'Category "{file}" deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting category: {str(e)}'
        })

@app.route('/config/<filename>')
def serve_config(filename):
    """Serve config files"""
    try:
        config_path = os.path.join('config', filename)
        if not os.path.exists(config_path):
            return jsonify({'error': 'File not found'}), 404
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data is None:
                data = {}
            return data
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test_categories')
def test_categories():
    """Test endpoint to debug category loading"""
    try:
        config_dir = 'config'
        result = {
            'config_dir_exists': os.path.exists(config_dir),
            'files_in_config': [],
            'categories_found': [],
            'load_categories_result': None,
            'load_categories_errors': []
        }
        
        # List all files in config directory
        if os.path.exists(config_dir):
            all_files = os.listdir(config_dir)
            result['files_in_config'] = all_files
            
            # Process each JSON file
            for filename in all_files:
                if filename.endswith('.json'):
                    file_path = os.path.join(config_dir, filename)
                    file_info = {
                        'filename': filename,
                        'file_base': filename[:-5],
                        'excluded': filename in ['dmp_structure.json', 'quick_comments.json'],
                        'file_exists': os.path.exists(file_path),
                        'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                        'json_valid': False,
                        'json_error': None,
                        'contains_category_data': False,
                        'category_keys': []
                    }
                    
                    # Try to load and validate JSON
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            file_info['json_valid'] = True
                            file_info['category_keys'] = list(data.keys())
                            
                            # Check if it contains category data (dict with DMP sections)
                            for key, value in data.items():
                                if not key.startswith('_') and isinstance(value, dict):
                                    file_info['contains_category_data'] = True
                                    break
                                    
                    except Exception as e:
                        file_info['json_error'] = str(e)
                    
                    result['categories_found'].append(file_info)
        
        # Test the actual list_categories logic
        try:
            categories = []
            if os.path.exists(config_dir):
                for filename in os.listdir(config_dir):
                    if filename.endswith('.json') and filename not in ['dmp_structure.json', 'quick_comments.json']:
                        file_base = filename[:-5]
                        category_name = file_base.replace('_', ' ').title()
                        categories.append({
                            'file': file_base,
                            'name': category_name
                        })
            
            result['load_categories_result'] = {
                'success': True,
                'categories': categories,
                'count': len(categories)
            }
        except Exception as e:
            result['load_categories_errors'].append(str(e))
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'failed'
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