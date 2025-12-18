from utils.extractor import DMPExtractor
import json

print("Final Verification Test")
print("=" * 80)

extractor = DMPExtractor(debug_mode=False)

result = extractor.process_file(
    'uploads/Data Management Plan_S2025.docx',
    'outputs'
)

print(f"Success: {result['success']}")

if result['success']:
    cache_file = f"outputs/cache/{result['cache_file']}"

    with open(cache_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("\nSection Status:")
    for section_id in ['1.1', '1.2', '2.1', '2.2', '3.1', '3.2', '4.1', '4.2', '5.1', '5.2', '5.3', '6.1', '6.2']:
        para = data[section_id]['paragraphs'][0]
        status = "[OK] HAS CONTENT" if para != "Not answered in the source document." else "[X] PLACEHOLDER"
        preview = para[:80] + "..." if len(para) > 80 else para
        print(f"  {section_id}: {status}")
        if status == "[OK] HAS CONTENT":
            print(f"       {preview}")
