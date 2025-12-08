#!/usr/bin/env python3
"""
Test DMP extraction on real files from pzd folder
Generates comprehensive statistics and analysis
"""
import os
import sys
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.extractor import DMPExtractor


def test_file(file_path, output_dir, debug=False):
    """Test extraction for a single file"""
    filename = os.path.basename(file_path)
    print(f"\n{'='*80}")
    print(f"Testing: {filename}")
    print(f"{'='*80}")

    extractor = DMPExtractor(debug_mode=debug)

    try:
        start_time = time.time()
        result = extractor.process_file(file_path, output_dir)
        elapsed = time.time() - start_time

        if not result.get('success'):
            print(f"[FAIL] {result.get('message')}")
            return {
                'filename': filename,
                'success': False,
                'error': result.get('message'),
                'processing_time': elapsed
            }

        # Load cache to analyze extraction quality
        cache_id = result.get('cache_id')
        cache_file = os.path.join(output_dir, f"cache_{cache_id}.json")

        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)

        # Calculate statistics
        sections_with_content = 0
        total_paragraphs = 0
        section_details = {}

        for key, value in cache_data.items():
            if key.startswith('_'):
                continue
            if isinstance(value, dict) and 'paragraphs' in value:
                para_count = len(value['paragraphs'])
                if para_count > 0:
                    sections_with_content += 1
                    total_paragraphs += para_count
                section_details[key] = {
                    'question': value.get('question', '')[:50] + '...',
                    'paragraph_count': para_count
                }

        unconnected_count = len(cache_data.get('_unconnected_text', []))
        metadata = cache_data.get('_metadata', {})

        extraction_rate = (sections_with_content / 14) * 100

        # Display results
        print(f"[OK] Processing time: {elapsed:.2f}s")
        print(f"[OK] Sections with content: {sections_with_content}/14 ({extraction_rate:.1f}%)")
        print(f"[OK] Total paragraphs: {total_paragraphs}")
        print(f"[INFO] Unconnected items: {unconnected_count}")
        print(f"[INFO] Metadata: {metadata}")

        # Show section breakdown
        if sections_with_content > 0:
            print(f"\n[DETAIL] Section breakdown:")
            for section_id, details in sorted(section_details.items()):
                if details['paragraph_count'] > 0:
                    print(f"  {section_id}: {details['paragraph_count']} paragraphs")

        return {
            'filename': filename,
            'success': True,
            'processing_time': elapsed,
            'sections_extracted': sections_with_content,
            'total_paragraphs': total_paragraphs,
            'unconnected_items': unconnected_count,
            'extraction_rate': extraction_rate,
            'cache_id': cache_id,
            'metadata': metadata,
            'section_details': section_details
        }

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            'filename': filename,
            'success': False,
            'error': str(e),
            'processing_time': time.time() - start_time
        }


def main():
    """Main test runner"""
    print("="*80)
    print("DMP EXTRACTOR: REAL FILES TEST")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    pzd_dir = os.path.join(os.path.dirname(__file__), 'pzd')
    output_dir = os.path.join(os.path.dirname(__file__), 'test_outputs')
    os.makedirs(output_dir, exist_ok=True)

    # Find all DOCX and PDF files
    test_files = []
    for filename in os.listdir(pzd_dir):
        if filename.endswith(('.docx', '.pdf')):
            test_files.append(os.path.join(pzd_dir, filename))

    print(f"\nFound {len(test_files)} files to test")
    print("-"*80)

    # Ask for debug mode
    debug_mode = input("\nEnable debug mode? (y/n): ").lower().strip() == 'y'

    # Run tests
    results = []
    for file_path in sorted(test_files):
        result = test_file(file_path, output_dir, debug=debug_mode)
        results.append(result)

    # Generate summary report
    print(f"\n{'='*80}")
    print("SUMMARY REPORT")
    print(f"{'='*80}\n")

    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]

    print(f"Total files tested: {len(results)}")
    print(f"  [OK] Successful: {len(successful)}")
    print(f"  [FAIL] Failed: {len(failed)}")

    if successful:
        avg_time = sum(r['processing_time'] for r in successful) / len(successful)
        avg_rate = sum(r['extraction_rate'] for r in successful) / len(successful)
        avg_paragraphs = sum(r['total_paragraphs'] for r in successful) / len(successful)
        avg_unconnected = sum(r['unconnected_items'] for r in successful) / len(successful)

        print(f"\n[STATISTICS] Averages (successful extractions):")
        print(f"  Processing time: {avg_time:.2f}s")
        print(f"  Extraction rate: {avg_rate:.1f}%")
        print(f"  Paragraphs per file: {avg_paragraphs:.1f}")
        print(f"  Unconnected items: {avg_unconnected:.1f}")

        # Extraction quality breakdown
        excellent = [r for r in successful if r['extraction_rate'] >= 90]
        good = [r for r in successful if 70 <= r['extraction_rate'] < 90]
        fair = [r for r in successful if 50 <= r['extraction_rate'] < 70]
        poor = [r for r in successful if r['extraction_rate'] < 50]

        print(f"\n[QUALITY] Extraction quality breakdown:")
        print(f"  Excellent (90-100%): {len(excellent)} files")
        print(f"  Good (70-89%): {len(good)} files")
        print(f"  Fair (50-69%): {len(fair)} files")
        print(f"  Poor (<50%): {len(poor)} files")

        # Best and worst performing files
        if successful:
            best = max(successful, key=lambda x: x['extraction_rate'])
            worst = min(successful, key=lambda x: x['extraction_rate'])

            print(f"\n[BEST] Best extraction:")
            print(f"  File: {best['filename']}")
            print(f"  Rate: {best['extraction_rate']:.1f}%")
            print(f"  Sections: {best['sections_extracted']}/14")

            print(f"\n[WORST] Worst extraction:")
            print(f"  File: {worst['filename']}")
            print(f"  Rate: {worst['extraction_rate']:.1f}%")
            print(f"  Sections: {worst['sections_extracted']}/14")

    if failed:
        print(f"\n[FAILED] Failed files:")
        for r in failed:
            print(f"  - {r['filename']}: {r.get('error', 'Unknown error')}")

    # Save detailed report
    report_path = os.path.join(output_dir, 'real_files_test_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'test_date': datetime.now().isoformat(),
            'total_files': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'statistics': {
                'avg_processing_time': avg_time if successful else 0,
                'avg_extraction_rate': avg_rate if successful else 0,
                'avg_paragraphs': avg_paragraphs if successful else 0,
                'avg_unconnected': avg_unconnected if successful else 0
            },
            'quality_breakdown': {
                'excellent': len(excellent) if successful else 0,
                'good': len(good) if successful else 0,
                'fair': len(fair) if successful else 0,
                'poor': len(poor) if successful else 0
            },
            'results': results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n[REPORT] Detailed report saved to: {report_path}")
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)


if __name__ == '__main__':
    main()
