from utils.extractor import DMPExtractor
import json

print("Testing process_file with debug logging")
print("=" * 80)

extractor = DMPExtractor(debug_mode=False)

result = extractor.process_file(
    'uploads/Data Management Plan_S2025.docx',
    'outputs'
)

print(f"\nResult: {result['success']}")
if result['success']:
    cache_file = f"outputs/cache/{result['cache_file']}"
    print(f"Cache file: {cache_file}")

    # Load and check section 1.1
    with open(cache_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"\nSection 1.1 in cache:")
    print(f"  Paragraphs: {data['1.1']['paragraphs']}")
