#!/usr/bin/env python3
"""
Phase 1.3: PZD Files Extraction Test
Tests the extraction mechanism with sample PZD files
"""
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, '/home/user/DMP-ART')

from utils.extractor import DMPExtractor

def test_file_extraction(file_path, output_dir='pzd/test_outputs'):
    """Test extraction for a single file"""
    print(f"\n{'='*80}")
    print(f"TESTING: {os.path.basename(file_path)}")
    print(f"{'='*80}\n")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Initialize extractor
    extractor = DMPExtractor()

    # Run extraction
    try:
        start_time = datetime.now()
        result = extractor.process_file(file_path, output_dir)
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        print(f"✅ SUCCESS - Processing completed in {processing_time:.2f} seconds")
        print(f"\nResult:")
        print(json.dumps(result, indent=2, ensure_ascii=False)[:500])

        # Load and analyze cache
        if result.get('success') and result.get('cache_id'):
            cache_file = os.path.join(output_dir, f"cache_{result['cache_id']}.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                # Analyze extraction quality
                sections_with_content = 0
                total_paragraphs = 0
                unconnected_count = 0

                for key, value in cache_data.items():
                    if key == '_unconnected_text':
                        unconnected_count = len(value)
                    elif isinstance(value, dict) and 'paragraphs' in value:
                        if value['paragraphs']:
                            sections_with_content += 1
                            total_paragraphs += len(value['paragraphs'])

                print(f"\n📊 EXTRACTION STATISTICS:")
                print(f"  - Sections with content: {sections_with_content}/14")
                print(f"  - Total paragraphs extracted: {total_paragraphs}")
                print(f"  - Unconnected text items: {unconnected_count}")
                print(f"  - Extraction rate: {(sections_with_content/14)*100:.1f}%")

                # Show sample content from each section
                print(f"\n📝 SAMPLE CONTENT:")
                for section_id in ['1.1', '2.1', '3.1', '4.1', '5.1', '6.1']:
                    if section_id in cache_data and cache_data[section_id].get('paragraphs'):
                        sample = cache_data[section_id]['paragraphs'][0][:100] + "..."
                        print(f"  {section_id}: {sample}")

                return {
                    'success': True,
                    'filename': os.path.basename(file_path),
                    'processing_time': processing_time,
                    'sections_extracted': sections_with_content,
                    'total_paragraphs': total_paragraphs,
                    'unconnected_items': unconnected_count,
                    'extraction_rate': (sections_with_content/14)*100,
                    'cache_id': result['cache_id']
                }

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'filename': os.path.basename(file_path),
            'error': str(e)
        }

def main():
    """Main test runner"""
    print("="*80)
    print("DMP-ART: PZD Files Extraction Test")
    print("Phase 1.3: Testing extraction mechanism")
    print("="*80)

    pzd_dir = '/home/user/DMP-ART/pzd'
    test_files = []

    # Find all test files
    for filename in os.listdir(pzd_dir):
        if filename.endswith(('.docx', '.pdf')):
            test_files.append(os.path.join(pzd_dir, filename))

    print(f"\nFound {len(test_files)} test files:")
    for f in test_files:
        print(f"  - {os.path.basename(f)}")

    # Run tests
    results = []
    for file_path in test_files:
        result = test_file_extraction(file_path)
        results.append(result)

    # Generate summary report
    print(f"\n{'='*80}")
    print("SUMMARY REPORT")
    print(f"{'='*80}\n")

    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]

    print(f"Tests completed: {len(results)}")
    print(f"  ✅ Successful: {len(successful)}")
    print(f"  ❌ Failed: {len(failed)}")

    if successful:
        avg_time = sum(r['processing_time'] for r in successful) / len(successful)
        avg_rate = sum(r['extraction_rate'] for r in successful) / len(successful)
        avg_paragraphs = sum(r['total_paragraphs'] for r in successful) / len(successful)

        print(f"\n📊 AVERAGES (Successful extractions):")
        print(f"  - Processing time: {avg_time:.2f} seconds")
        print(f"  - Extraction rate: {avg_rate:.1f}%")
        print(f"  - Paragraphs per file: {avg_paragraphs:.1f}")

    if failed:
        print(f"\n❌ FAILED FILES:")
        for r in failed:
            print(f"  - {r['filename']}: {r.get('error', 'Unknown error')}")

    # Save detailed report
    report_path = os.path.join(pzd_dir, 'extraction_test_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'test_date': datetime.now().isoformat(),
            'total_files': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'results': results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Detailed report saved to: {report_path}")
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
