from utils.extractor import DMPExtractor
from docx import Document

print("Testing exact process_docx flow")
print("=" * 80)

# Initialize extractor
extractor = DMPExtractor(debug_mode=False)

# Load document
doc = Document('uploads/Data Management Plan_S2025.docx')

# Extract content exactly as process_docx does
formatted_paragraphs = []

# Process paragraphs
for paragraph in doc.paragraphs:
    formatted_text = extractor.extract_formatted_text(paragraph)
    if formatted_text.strip():
        formatted_paragraphs.append(formatted_text)

# Process tables
table_content = extractor.extract_table_content(doc)
formatted_paragraphs.extend(table_content)

print(f"\nTotal formatted paragraphs: {len(formatted_paragraphs)}")

# Find DMP content (simplified - assume starts at index 0 for this test)
start_idx = 0
for i, para in enumerate(formatted_paragraphs):
    clean_para = para.replace("UNDERLINED:", "").replace("BOLD:", "").replace("UNDERLINED_BOLD:", "").strip()
    if "Data Management Plan" in clean_para or "PLAN ZARZĄDZANIA DANYMI" in clean_para:
        start_idx = i + 1
        print(f"Found DMP start at paragraph {i}")
        break

dmp_paragraphs = formatted_paragraphs[start_idx:]

# Filter meaningful content
meaningful_content = []
for para in dmp_paragraphs:
    if not para.strip():
        continue

    clean_para = para
    if "BOLD:" in para or "UNDERLINED:" in para or "UNDERLINED_BOLD:" in para:
        clean_para = para.replace("BOLD:", "").replace("UNDERLINED:", "").replace("UNDERLINED_BOLD:", "").strip()

    if extractor.should_skip_text(clean_para, is_pdf=False):
        continue

    if len(clean_para) > 5:
        meaningful_content.append(para)

print(f"Meaningful content items: {len(meaningful_content)}")
print(f"\nFirst 5 meaningful items:")
for i, item in enumerate(meaningful_content[:5]):
    print(f"{i+1}. [{len(item)} chars] {item[:100]}...")

# Call improve_content_assignment
print("\n" + "=" * 80)
print("CALLING improve_content_assignment")
print("=" * 80)

section_content, tagged_content, unconnected_text = extractor.improve_content_assignment(
    meaningful_content, is_pdf=False
)

# Check section 1.1
section_1 = '1. Data description and collection or re-use of existing data'
question_11 = 'How will new data be collected or produced and/or how will existing data be re-used?'

print(f"\nSection 1.1 paragraphs from improve_content_assignment: {len(section_content[section_1][question_11])}")
if section_content[section_1][question_11]:
    print(f"First paragraph (first 200 chars): {section_content[section_1][question_11][0][:200]}")

    # Now clean it
    cleaned = extractor.clean_extracted_paragraphs(section_content[section_1][question_11])
    print(f"\nAfter clean_extracted_paragraphs: {len(cleaned)} paragraphs")
    if cleaned:
        print(f"First cleaned paragraph (first 200 chars): {cleaned[0][:200]}")
    else:
        print("*** PROBLEM: Cleaning removed all content! ***")
