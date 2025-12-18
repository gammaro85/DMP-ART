from utils.extractor import DMPExtractor
import json

print("Testing fallback logic with Data Management Plan_S2025.docx")
print("=" * 80)

extractor = DMPExtractor(debug_mode=False)
result = extractor.process_file('uploads/Data Management Plan_S2025.docx', 'outputs')

if result['success']:
    print(f"\nExtraction SUCCESS")
    print(f"Cache file: {result['cache_file']}")

    # Load cache
    cache_path = f"outputs/cache/{result['cache_file']}"
    with open(cache_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("\n" + "=" * 80)
    print("SECTION CONTENT ANALYSIS")
    print("=" * 80)

    # Check each section
    for section_id in ['1.1', '1.2', '2.1', '2.2', '3.1', '3.2', '4.1', '4.2', '5.1', '5.2', '5.3', '5.4', '6.1', '6.2']:
        paragraphs = data[section_id]['paragraphs']
        if paragraphs and paragraphs[0] != "Not answered in the source document.":
            print(f"\n{section_id}: {len(paragraphs)} paragraph(s)")
            print(f"  First 100 chars: {paragraphs[0][:100]}...")

    print("\n" + "=" * 80)
    print("UNCONNECTED TEXT ANALYSIS")
    print("=" * 80)

    unconnected = data.get('_unconnected_text', [])
    print(f"\nTotal unconnected items: {len(unconnected)}")

    if unconnected:
        for i, item in enumerate(unconnected[:3]):  # Show first 3
            print(f"\nItem {i+1}:")
            print(f"  Type: {item['type']}")
            print(f"  First 150 chars: {item['text'][:150]}...")

    print("\n" + "=" * 80)
    print("EXPECTED vs ACTUAL")
    print("=" * 80)
    print("\nExpected: Section 1.2 should have content about data types/formats/volumes")
    print(f"Actual: Section 1.2 has {len(data['1.2']['paragraphs'])} paragraph(s)")
    if data['1.2']['paragraphs'][0] == "Not answered in the source document.":
        print("  STATUS: FAILED - Still has placeholder")
    else:
        print(f"  STATUS: SUCCESS - Has content: {data['1.2']['paragraphs'][0][:100]}...")

    print("\nExpected: Section 6.1 should have ONLY content about data steward")
    print(f"Actual: Section 6.1 has {len(data['6.1']['paragraphs'])} paragraph(s)")
    if len(data['6.1']['paragraphs']) > 2:
        print(f"  STATUS: FAILED - Has too many paragraphs (likely contains other sections' content)")
    else:
        print(f"  STATUS: SUCCESS - Has appropriate amount of content")

else:
    print(f"\nExtraction FAILED: {result.get('message', 'Unknown error')}")
