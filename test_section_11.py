from utils.extractor import DMPExtractor
from docx import Document

print("Testing section 1.1 assignment")
print("=" * 80)

# Initialize extractor
extractor = DMPExtractor(debug_mode=False)

# Extract content
doc = Document('uploads/Data Management Plan_S2025.docx')
all_content = extractor.extract_table_content(doc)

print(f"\nTotal items: {len(all_content)}")
print(f"\nFirst 3 items:")
for i in range(min(3, len(all_content))):
    item = all_content[i]
    first_line = item.split('\n')[0] if '\n' in item else item
    print(f"\nItem {i}:")
    print(f"  First line: {first_line[:100]}")
    print(f"  Total length: {len(item)} chars")
    print(f"  Lines: {len(item.split(chr(10)))}")

# Process with improve_content_assignment
print("\n" + "=" * 80)
print("PROCESSING WITH improve_content_assignment")
print("=" * 80)

section_content, tagged_content, unconnected = extractor.improve_content_assignment(all_content, is_pdf=False)

print(f"\nSection 1.1 paragraphs: {len(section_content['1. Data description and collection or re-use of existing data']['How will new data be collected or produced and/or how will existing data be re-used?'])}")
print(f"Section 1.2 paragraphs: {len(section_content['1. Data description and collection or re-use of existing data']['What data (for example the types, formats, and volumes) will be collected or produced?'])}")
print(f"Unconnected: {len(unconnected)}")

if section_content['1. Data description and collection or re-use of existing data']['How will new data be collected or produced and/or how will existing data be re-used?']:
    print(f"\nSection 1.1 first paragraph (first 200 chars):")
    print(section_content['1. Data description and collection or re-use of existing data']['How will new data be collected or produced and/or how will existing data be re-used?'][0][:200])
