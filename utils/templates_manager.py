# utils/templates_manager.py
import json
import os

class TemplatesManager:
    def __init__(self, templates_file='templates.json'):
        self.templates_file = templates_file
        self.templates = self._load_templates()
    
    def _load_templates(self):
        """Load templates from JSON file or return defaults if file doesn't exist"""
        if os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading templates: {str(e)}")
                return self._get_default_templates()
        else:
            return self._get_default_templates()
    
    def _get_default_templates(self):
        """Return the default templates"""
        return {
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
    
    def save_templates(self, templates):
        """Save templates to the JSON file"""
        # Update only the templates that were changed
        for key, value in templates.items():
            if key in self.templates:
                # If we're receiving a string, update only the template text
                if isinstance(value, str):
                    self.templates[key]["template"] = value
                # If we're receiving a dict, update the whole template
                elif isinstance(value, dict) and "template" in value:
                    self.templates[key] = value
            else:
                # Handle adding new templates
                if isinstance(value, str):
                    self.templates[key] = {
                        "question": f"Question {key}",
                        "template": value
                    }
                elif isinstance(value, dict):
                    self.templates[key] = value
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.templates_file), exist_ok=True)
            
            # Save to file
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving templates: {str(e)}")
            return False
    
    def get_templates(self):
        """Return all templates"""
        return self.templates