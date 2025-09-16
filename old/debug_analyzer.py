#!/usr/bin/env python3
"""
DMP ART Debug Analyzer
Comprehensive script to find dead code, inconsistencies, and dead references
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List
import ast

class DebugAnalyzer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = []
        self.files_analyzed = 0
        
        # Patterns to identify different types of issues
        self.patterns = {
            'dead_functions': [],
            'unused_variables': [],
            'dead_imports': [],
            'inconsistent_naming': [],
            'dead_css_classes': [],
            'dead_js_functions': [],
            'missing_files': [],
            'inconsistent_themes': []
        }
    
    def analyze_project(self):
        """Main analysis method"""
        print("🔍 Starting DMP ART Debug Analysis...")
        print("=" * 50)
        
        # 1. Check file structure integrity
        self.check_file_structure()
        
        # 2. Analyze Python files
        self.analyze_python_files()
        
        # 3. Analyze JavaScript files
        self.analyze_javascript_files()
        
        # 4. Analyze HTML templates
        self.analyze_html_templates()
        
        # 5. Analyze CSS files
        self.analyze_css_files()
        
        # 6. Check for cross-file consistency
        self.check_cross_file_consistency()
        
        # 7. Check theme implementation consistency
        self.check_theme_consistency()
        
        # 8. Generate report
        self.generate_report()
    
    def check_file_structure(self):
        """Check if all expected files exist"""
        print("\n📁 Checking file structure...")
        
        expected_files = [
            "app.py",
            "requirements.txt",
            "static/js/script.js",
            "static/js/dark-mode.js",
            "static/js/template_editor.js",
            "static/css/style.css",
            "templates/index.html",
            "templates/review.html",
            "templates/results.html",
            "templates/template_editor.html",
            "templates/documentation.html",
            "utils/extractor.py",
            "config/dmp_structure.json",
            "config/key_phrases.json"
        ]
        
        missing_files = []
        for file_path in expected_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                self.add_issue("missing_files", f"Missing file: {file_path}")
        
        if missing_files:
            print(f"❌ Found {len(missing_files)} missing files")
        else:
            print("✅ All expected files present")
    
    def analyze_python_files(self):
        """Analyze Python files for issues"""
        print("\n🐍 Analyzing Python files...")
        
        python_files = list(self.project_root.glob("**/*.py"))
        
        for py_file in python_files:
            if py_file.name.startswith('.'):
                continue
                
            self.files_analyzed += 1
            self.analyze_python_file(py_file)
    
    def analyze_python_file(self, file_path: Path):
        """Analyze individual Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST for detailed analysis
            try:
                tree = ast.parse(content)
                self.analyze_python_ast(tree, file_path)
            except SyntaxError as e:
                self.add_issue("syntax_errors", f"Syntax error in {file_path}: {e}")
            
            # Check for common issues
            self.check_python_imports(content, file_path)
            self.check_python_functions(content, file_path)
            
        except Exception as e:
            self.add_issue("file_read_errors", f"Error reading {file_path}: {e}")
    
    def analyze_python_ast(self, tree: ast.AST, file_path: Path):
        """Analyze Python AST for dead code"""
        functions_defined = set()
        functions_called = set()
        imports = set()
        
        class FunctionVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                functions_defined.add(node.name)
                self.generic_visit(node)
            
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    functions_called.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    functions_called.add(node.func.attr)
                self.generic_visit(node)
            
            def visit_Import(self, node):
                for alias in node.names:
                    imports.add(alias.name)
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                for alias in node.names:
                    imports.add(alias.name)
                self.generic_visit(node)
        
        visitor = FunctionVisitor()
        visitor.visit(tree)
        
        # Find potentially dead functions
        dead_functions = functions_defined - functions_called
        for func in dead_functions:
            if not func.startswith('_') and func not in ['main', 'init', 'run']:
                self.add_issue("dead_functions", f"Potentially unused function '{func}' in {file_path}")
    
    def check_python_imports(self, content: str, file_path: Path):
        """Check for unused imports"""
        import_lines = re.findall(r'^(?:from .+ )?import .+$', content, re.MULTILINE)
        
        for line in import_lines:
            # Extract imported names
            if 'from' in line:
                match = re.search(r'import (.+)$', line)
                if match:
                    imported_items = [item.strip() for item in match.group(1).split(',')]
            else:
                match = re.search(r'import (.+)$', line)
                if match:
                    imported_items = [item.strip().split(' as ')[0] for item in match.group(1).split(',')]
            
            # Check if imports are used (basic check)
            for item in imported_items:
                if item not in content.replace(line, ''):
                    self.add_issue("dead_imports", f"Potentially unused import '{item}' in {file_path}")
    
    def check_python_functions(self, content: str, file_path: Path):
        """Check for function-related issues"""
        # Find function definitions
        functions = re.findall(r'def (\w+)\(', content)
        
        # Check for inconsistent naming
        for func in functions:
            if not re.match(r'^[a-z_][a-z0-9_]*$', func):
                self.add_issue("inconsistent_naming", f"Function '{func}' doesn't follow snake_case in {file_path}")
    
    def analyze_javascript_files(self):
        """Analyze JavaScript files for issues"""
        print("\n📜 Analyzing JavaScript files...")
        
        js_files = list(self.project_root.glob("**/*.js"))
        
        for js_file in js_files:
            if js_file.name.startswith('.'):
                continue
                
            self.files_analyzed += 1
            self.analyze_javascript_file(js_file)
    
    def analyze_javascript_file(self, file_path: Path):
        """Analyze individual JavaScript file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for dead functions
            self.check_js_functions(content, file_path)
            
            # Check for console.log statements (should be removed in production)
            console_logs = re.findall(r'console\.log\(.*?\)', content)
            if console_logs:
                self.add_issue("debug_code", f"Found {len(console_logs)} console.log statements in {file_path}")
            
            # Check for theme-related inconsistencies
            self.check_js_theme_code(content, file_path)
            
        except Exception as e:
            self.add_issue("file_read_errors", f"Error reading {file_path}: {e}")
    
    def check_js_functions(self, content: str, file_path: Path):
        """Check JavaScript functions for issues"""
        # Find function definitions
        functions_defined = set()
        functions_called = set()
        
        # Function definitions
        func_defs = re.findall(r'function\s+(\w+)\s*\(', content)
        functions_defined.update(func_defs)
        
        # Arrow functions assigned to variables
        arrow_funcs = re.findall(r'(?:const|let|var)\s+(\w+)\s*=.*?=>', content)
        functions_defined.update(arrow_funcs)
        
        # Function calls
        func_calls = re.findall(r'(\w+)\s*\(', content)
        functions_called.update(func_calls)
        
        # Check for potentially dead functions
        potentially_dead = functions_defined - functions_called
        for func in potentially_dead:
            # Skip common utility functions and event handlers
            if func not in ['DOMContentLoaded', 'addEventListener', 'toggleTheme', 'initializeTemplateEditor']:
                self.add_issue("dead_js_functions", f"Potentially unused function '{func}' in {file_path}")
    
    def check_js_theme_code(self, content: str, file_path: Path):
        """Check for theme-related code consistency"""
        # Check for removed theme notification references
        if 'showThemeNotification' in content:
            self.add_issue("dead_references", f"Reference to removed 'showThemeNotification' function in {file_path}")
        
        # Check for icon references that should be removed
        icon_patterns = [
            r'theme-icon',
            r'🌙',
            r'☀️',
            r'textContent.*=.*[\'"]🌙[\'"]',
            r'textContent.*=.*[\'"]☀️[\'"]'
        ]
        
        for pattern in icon_patterns:
            if re.search(pattern, content):
                self.add_issue("inconsistent_themes", f"Found theme icon reference in {file_path}: {pattern}")
    
    def analyze_html_templates(self):
        """Analyze HTML template files"""
        print("\n📄 Analyzing HTML templates...")
        
        html_files = list(self.project_root.glob("templates/*.html"))
        
        for html_file in html_files:
            self.files_analyzed += 1
            self.analyze_html_file(html_file)
    
    def analyze_html_file(self, file_path: Path):
        """Analyze individual HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for theme toggle consistency
            self.check_html_theme_toggle(content, file_path)
            
            # Check for dead CSS classes
            self.check_html_css_classes(content, file_path)
            
            # Check for missing alt attributes on images
            img_tags = re.findall(r'<img[^>]*>', content)
            for img in img_tags:
                if 'alt=' not in img:
                    self.add_issue("accessibility", f"Image without alt attribute in {file_path}: {img}")
            
        except Exception as e:
            self.add_issue("file_read_errors", f"Error reading {file_path}: {e}")
    
    def check_html_theme_toggle(self, content: str, file_path: Path):
        """Check theme toggle implementation in HTML"""
        # Check for icon spans that should be removed
        if 'theme-icon' in content:
            self.add_issue("inconsistent_themes", f"Found theme-icon reference in {file_path}")
        
        # Check for proper theme toggle structure
        if 'theme-toggle' in content:
            # Should only have theme-text span, no icons
            theme_toggle_match = re.search(r'<div[^>]*class[^>]*theme-toggle[^>]*>.*?</div>', content, re.DOTALL)
            if theme_toggle_match:
                toggle_content = theme_toggle_match.group(0)
                if '🌙' in toggle_content or '☀️' in toggle_content:
                    self.add_issue("inconsistent_themes", f"Theme toggle contains emoji icons in {file_path}")
    
    def check_html_css_classes(self, content: str, file_path: Path):
        """Check for potentially unused CSS classes"""
        # Extract class names from HTML
        classes_used = set()
        class_matches = re.findall(r'class=["\']([^"\']+)["\']', content)
        for match in class_matches:
            classes_used.update(match.split())
        
        # Store for cross-file analysis
        if not hasattr(self, 'html_classes'):
            self.html_classes = {}
        self.html_classes[file_path.name] = classes_used
    
    def analyze_css_files(self):
        """Analyze CSS files for issues"""
        print("\n🎨 Analyzing CSS files...")
        
        css_files = list(self.project_root.glob("**/*.css"))
        
        for css_file in css_files:
            self.files_analyzed += 1
            self.analyze_css_file(css_file)
    
    def analyze_css_file(self, file_path: Path):
        """Analyze individual CSS file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract CSS class definitions
            classes_defined = set()
            class_matches = re.findall(r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)', content)
            classes_defined.update(class_matches)
            
            # Store for cross-file analysis
            if not hasattr(self, 'css_classes'):
                self.css_classes = {}
            self.css_classes[file_path.name] = classes_defined
            
            # Check for theme-related inconsistencies
            self.check_css_theme_vars(content, file_path)
            
            # Check for duplicate selectors
            self.check_css_duplicates(content, file_path)
            
        except Exception as e:
            self.add_issue("file_read_errors", f"Error reading {file_path}: {e}")
    
    def check_css_theme_vars(self, content: str, file_path: Path):
        """Check CSS theme variables for consistency"""
        # Check if the updated color scheme is implemented
        expected_dark_colors = {
            '--secondary-color: #375D78',
            '--accent-color: #E86B6B',
            '--success-color: #408A8B'
        }
        
        for color in expected_dark_colors:
            if color not in content:
                self.add_issue("inconsistent_themes", f"Missing updated dark theme color '{color}' in {file_path}")
    
    def check_css_duplicates(self, content: str, file_path: Path):
        """Check for duplicate CSS selectors"""
        selectors = re.findall(r'([^{}]+){', content)
        selector_counts = {}
        
        for selector in selectors:
            selector = selector.strip()
            if selector:
                selector_counts[selector] = selector_counts.get(selector, 0) + 1
        
        for selector, count in selector_counts.items():
            if count > 1:
                self.add_issue("duplicate_css", f"Duplicate selector '{selector}' appears {count} times in {file_path}")
    
    def check_cross_file_consistency(self):
        """Check consistency across different file types"""
        print("\n🔗 Checking cross-file consistency...")
        
        # Compare CSS classes defined vs used
        if hasattr(self, 'css_classes') and hasattr(self, 'html_classes'):
            all_css_classes = set()
            for classes in self.css_classes.values():
                all_css_classes.update(classes)
            
            all_html_classes = set()
            for classes in self.html_classes.values():
                all_html_classes.update(classes)
            
            # Find unused CSS classes
            unused_css = all_css_classes - all_html_classes
            for css_class in unused_css:
                # Skip utility classes and pseudo-classes
                if not css_class.startswith(('hover', 'focus', 'active', 'before', 'after')):
                    self.add_issue("dead_css_classes", f"Potentially unused CSS class: .{css_class}")
            
            # Find undefined CSS classes used in HTML
            undefined_css = all_html_classes - all_css_classes
            for html_class in undefined_css:
                self.add_issue("missing_css", f"CSS class used but not defined: .{html_class}")
    
    def check_theme_consistency(self):
        """Check theme implementation consistency"""
        print("\n🎭 Checking theme consistency...")
        
        # Check all HTML files for consistent theme toggle implementation
        html_files = list(self.project_root.glob("templates/*.html"))
        
        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check theme toggle structure
                if 'theme-toggle' in content:
                    # Should have onclick="toggleTheme()"
                    if 'onclick="toggleTheme()"' not in content:
                        self.add_issue("inconsistent_themes", f"Theme toggle missing onclick handler in {html_file.name}")
                    
                    # Should have theme-text span
                    if 'id="theme-text"' not in content:
                        self.add_issue("inconsistent_themes", f"Theme toggle missing theme-text span in {html_file.name}")
                    
                    # Should NOT have theme-icon
                    if 'theme-icon' in content:
                        self.add_issue("inconsistent_themes", f"Theme toggle has unwanted theme-icon in {html_file.name}")
            
            except Exception as e:
                self.add_issue("file_read_errors", f"Error reading {html_file}: {e}")
    
    def add_issue(self, category: str, description: str):
        """Add an issue to the analysis results"""
        self.issues.append({
            'category': category,
            'description': description
        })
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("\n" + "=" * 50)
        print("📊 DEBUG ANALYSIS REPORT")
        print("=" * 50)
        
        print(f"\n📈 Summary:")
        print(f"  Files analyzed: {self.files_analyzed}")
        print(f"  Total issues found: {len(self.issues)}")
        
        # Group issues by category
        issues_by_category = {}
        for issue in self.issues:
            category = issue['category']
            if category not in issues_by_category:
                issues_by_category[category] = []
            issues_by_category[category].append(issue['description'])
        
        # Print issues by category
        for category, issue_list in issues_by_category.items():
            print(f"\n🔍 {category.upper().replace('_', ' ')} ({len(issue_list)} issues):")
            for i, issue in enumerate(issue_list, 1):
                print(f"  {i}. {issue}")
        
        # Generate recommendations
        self.generate_recommendations(issues_by_category)
        
        # Save detailed report to file
        self.save_detailed_report(issues_by_category)
    
    def generate_recommendations(self, issues_by_category: Dict[str, List[str]]):
        """Generate actionable recommendations"""
        print(f"\n💡 RECOMMENDATIONS:")
        print("-" * 30)
        
        if 'dead_functions' in issues_by_category:
            print("• Remove or refactor unused functions to reduce code bloat")
        
        if 'dead_imports' in issues_by_category:
            print("• Clean up unused imports to improve load times")
        
        if 'inconsistent_themes' in issues_by_category:
            print("• Fix theme implementation inconsistencies for better UX")
        
        if 'dead_css_classes' in issues_by_category:
            print("• Remove unused CSS classes to reduce file size")
        
        if 'debug_code' in issues_by_category:
            print("• Remove console.log statements before production")
        
        if 'missing_files' in issues_by_category:
            print("• Create missing files or update file structure")
        
        print("• Run this analyzer regularly during development")
        print("• Consider setting up automated code quality checks")
    
    def save_detailed_report(self, issues_by_category: Dict[str, List[str]]):
        """Save detailed report to JSON file"""
        report_data = {
            'analysis_summary': {
                'files_analyzed': self.files_analyzed,
                'total_issues': len(self.issues),
                'categories': list(issues_by_category.keys())
            },
            'issues_by_category': issues_by_category,
            'all_issues': self.issues
        }
        
        report_file = self.project_root / 'debug_analysis_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed report saved to: {report_file}")

def main():
    """Main execution function"""
    analyzer = DebugAnalyzer()
    analyzer.analyze_project()
    
    print(f"\n✅ Analysis complete! Check 'debug_analysis_report.json' for detailed results.")

if __name__ == "__main__":
    main()