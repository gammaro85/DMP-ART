# DMP ART (DMP Assessment and Response Tool)

## Preliminary Documentation - Alpha Version 0.5

### May 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [Current Status and Limitations](#current-status-and-limitations)
3. [System Requirements](#system-requirements)
4. [Installation](#installation)
5. [User Guide](#user-guide)
6. [Technical Architecture](#technical-architecture)
7. [Known Issues](#known-issues)
8. [Troubleshooting](#troubleshooting)
9. [Future Development](#future-development)

---

## Introduction

DMP ART (DMP Assessment and Response Tool) is a specialized web application designed to assist with the assessment of Data Management Plans (DMPs) from grant proposals submitted to the National Science Centre (NCN) through the OSF system. OSF (Obsługa Strumieni Finansowania / Funding Stream Support System) is part of Poland's Integrated System of Services for Science/Research (Zintegrowany System Usług dla Nauki) and serves as the primary platform for submitting and managing NCN grant applications.

This early-stage tool aims to support research administrators and grant officers at Polish institutions by attempting to extract DMP content from OSF-exported PDF documents of NCN proposals, providing a structured review interface, and generating standardized feedback.

### Key Features

- Basic extraction of DMP content from NCN grant proposals exported from Polish OSF
- Attempt to organize content by standard DMP sections
- Simple keyword-based tagging of concepts
- Customizable feedback templates
- PDF-to-Word conversion for manual editing when automatic extraction fails

---

## Current Status and Limitations

**Important:** DMP ART is currently in alpha stage (version 0.5) with significant limitations. Users should be aware that:

- **NCN/OSF-Specific:** The tool is specifically designed for PDFs of NCN grant proposals exported from the OSF system and will not work properly with other DMP formats or grant applications.
- **Extraction Reliability:** Text recognition and extraction are inconsistent and frequently fail, especially with complex formatting or non-standard sections in the NCN proposal PDFs.
- **Limited Recognition:** The system often fails to correctly identify DMP sections even when they follow expected patterns in the NCN template.
- **Manual Intervention Required:** In many cases, manual review and correction of the extracted content will be necessary.
- **Language Constraints:** The system expects content primarily in Polish or English, with Polish OSF section headers typical of NCN proposals.
- **Export Issues:** The export functionality is basic and unreliable in the current version.
- **Development Status:** This is an early prototype intended for testing and feedback, not production use.

---

## System Requirements

### Server Requirements

- Python 3.8 or higher
- 2GB RAM minimum
- 500MB storage space for application and dependencies
- Additional storage space for uploaded files and generated documents

### Client Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- PDF files under 16MB in size
- PDF files must be direct exports of NCN grant proposals from the OSF system

### Dependencies

The application requires the following Python packages:
- Flask==2.3.3
- PyPDF2==3.0.1
- python-docx==0.8.11
- Werkzeug==2.3.7

These dependencies are listed in the provided `requirements.txt` file.

---

## Installation

### Development Installation

1. Clone or download the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the application in development mode:
   ```
   python app.py
   ```
6. Access the application at http://127.0.0.1:5000

**Note:** This installation is intended for development and testing only. The application is not yet ready for production deployment.

---

## User Guide

### Home Screen

The home screen provides a simple interface for uploading PDF files containing Data Management Plans.

1. Click "Select File" or drag and drop a PDF file into the designated area
   - **Important:** Only use PDFs of NCN grant proposals exported directly from the OSF system
2. Once a file is selected, click "Extract & Review DMP" to process the file
3. The application will attempt to extract the DMP content and structure it for review
4. Be prepared for extraction failures, which are common in the current version

### Review Interface

If extraction is partially successful, the review interface will show:

1. DMP content organized by sections (which may be incomplete or incorrectly categorized)
2. Feedback text areas for each section
3. Pre-defined comment templates accessible via comment buttons
4. Copy/Reset buttons for managing feedback text

**Note:** Due to extraction limitations, many sections may be empty or contain incorrectly categorized content. Always verify the extracted content against the original PDF.

### Template Editor

Basic template customization is available:

1. Access the template editor by clicking "Customize Templates" on the home screen
2. Edit template text for each standard DMP question
3. Click "Save Template" to save individual templates
4. Click "Save All Templates" to save all changes at once

**Note:** Template changes are not persistent and will reset when the application restarts.

---

## Technical Architecture

DMP ART uses a basic architecture:

### Backend Components

- **Flask Application (`app.py`)**: The main web application that handles routes and uploads
- **DMP Extractor (`utils/extractor.py`)**: Attempts to process NCN proposal PDFs from OSF and extract DMP sections
- **File Storage**: Manages uploaded PDFs and generated documents in local directories

### PDF Processing Approach

The DMP Extractor attempts to:

1. Locate the DMP section in NCN/OSF PDFs using specific markers like "PLAN ZARZĄDZANIA DANYMI" or "DATA MANAGEMENT PLAN"
2. Extract text using PyPDF2 (with limited reliability)
3. Match content to predefined DMP sections based on headings and keywords
4. Apply basic tagging based on simple keyword matching

**Note:** The current extraction process is rudimentary and frequently fails to correctly identify and categorize content from NCN proposals.

---

## Known Issues

The following major issues are present in the current version:

1. **Extraction Failures:** The system frequently fails to correctly identify and extract DMP content from NCN proposal PDFs exported from OSF.

2. **Section Recognition:** Even when content is extracted, it's often incorrectly assigned to DMP sections.

3. **Text Formatting:** Formatting is lost during extraction, and text may appear jumbled or contain artifacts.

4. **Incomplete Extraction:** The system may miss significant portions of the DMP content.

5. **NCN/OSF-Specific Limitations:** The tool only works with NCN proposals from the Polish OSF system and cannot process other DMP formats.

6. **No Data Persistence:** All data, including templates and feedback, is lost when the application restarts.

7. **Language Issues:** Mixed Polish and English content in NCN proposals may cause unpredictable behavior.

8. **Export Reliability:** The export functionality is basic and often produces unusable results.

---

## Troubleshooting

### When Extraction Fails Completely

If the system cannot extract any DMP content:

1. Verify that the PDF is a direct export of an NCN grant proposal from the OSF system
2. Check that the PDF contains a complete "PLAN ZARZĄDZANIA DANYMI" or "DATA MANAGEMENT PLAN" section as required by NCN
3. Try re-downloading the PDF from OSF to ensure it's not corrupted
4. If possible, export the PDF again using different settings in OSF

### When Extraction Is Partial or Incorrect

If content is extracted but is incomplete or incorrectly categorized:

1. Download the Word document and manually edit it to correct issues
2. For critical DMPs, consider manually copying content from the PDF instead
3. Look for "start marks" and "end marks" in the console logs, which indicate where the system is trying to find DMP content
4. Try using the template editor to add phrases that match the actual content of your NCN proposal DMP

### When No Sections Are Recognized

If the system extracts text but doesn't recognize any sections:

1. Check the PDF structure to ensure sections follow standard NCN DMP headings
2. Look for unusual formatting in the PDF that might interfere with text extraction
3. Try a different NCN proposal PDF to determine if the issue is specific to one document

---

## Future Development

The current version is an early prototype with significant limitations. Future development plans include:

### Short-term Improvements (if development continues)

- Improved text extraction from NCN proposal PDFs exported from OSF
- Better section recognition specific to NCN DMP structure
- Persistent storage for templates and settings
- More comprehensive error handling and user feedback
- Support for different NCN funding program templates (OPUS, SONATA, etc.)

### Long-term Vision

- Machine learning-based text extraction and categorization
- Support for multiple DMP formats beyond NCN/OSF
- Integration with institutional systems
- Collaborative review features
- Advanced analytics and recommendations for NCN proposals

**Note:** Development continuity depends on user feedback and resource availability. This alpha version is primarily intended to gauge interest and collect feedback on the concept.

---

*This documentation was prepared for DMP ART alpha version 0.5, May 2025. This is an early prototype with significant limitations. Please provide feedback on the concept and functionality to help guide future development.*
