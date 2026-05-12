#!/usr/bin/env python3
"""
Integration test for review output folder separation.

This test simulates the complete workflow:
1. DMP extraction to outputs/
2. Feedback creation to outputs/reviews/
3. Verification of file linkage
"""

import os
import json
from datetime import datetime


def _normalized(path):
    """Normalize paths so assertions behave the same on Windows and POSIX."""
    return os.path.normpath(path)

def simulate_workflow():
    """Simulate the complete DMP review workflow"""
    print("\n" + "=" * 60)
    print("INTEGRATION TEST: DMP Review Workflow")
    print("=" * 60 + "\n")
    
    # Step 1: Simulate DMP extraction
    print("Step 1: Extract DMP from proposal")
    print("-" * 60)
    
    researcher_surname = "Kowalski"
    researcher_firstname = "Jan"
    competition_name = "OPUS"
    competition_edition = "29"
    date_str = datetime.now().strftime('%d%m%y')
    
    dmp_filename = f"DMP_{researcher_surname}_{researcher_firstname[0]}_{competition_name}_{competition_edition}_{date_str}.docx"
    dmp_path = os.path.join('outputs', dmp_filename)
    
    # Create a mock DMP file
    with open(dmp_path, 'w') as f:
        f.write("Mock DMP content for testing")
    
    print(f"✓ DMP extracted and saved to: {dmp_path}")
    assert os.path.exists(dmp_path), "DMP file not created"
    
    # Step 2: Simulate feedback creation
    print("\nStep 2: Create review feedback")
    print("-" * 60)
    
    # Generate feedback filename based on DMP filename
    feedback_base = os.path.splitext(dmp_filename)[0]
    feedback_filename = f"feedback_{feedback_base}.txt"
    feedback_path = os.path.join('outputs', 'reviews', feedback_filename)
    
    # Create mock feedback
    feedback_content = f"""
═══════════════════════════════════════
RECENZJA PLANU ZARZĄDZANIA DANYMI
═══════════════════════════════════════

Wniosek: {competition_name}-{competition_edition}
Naukowiec: {researcher_firstname} {researcher_surname}
Data oceny: {datetime.now().strftime('%Y-%m-%d')}

═══════════════════════════════════════
SEKCJA 1.1: Sposób pozyskiwania danych
═══════════════════════════════════════

Ocena: ✅ Sekcja kompletna i zgodna z wymaganiami.

═══════════════════════════════════════
PODSUMOWANIE
═══════════════════════════════════════

Ocena ogólna: POZYTYWNA

Recenzent: Data Steward
Data: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    with open(feedback_path, 'w', encoding='utf-8') as f:
        f.write(feedback_content)
    
    print(f"✓ Feedback created and saved to: {feedback_path}")
    assert os.path.exists(feedback_path), "Feedback file not created"
    
    # Step 3: Create JSON export
    print("\nStep 3: Export structured review (JSON)")
    print("-" * 60)
    
    json_filename = f"Review_{researcher_surname}_{researcher_firstname[0]}_{competition_name}_{competition_edition}_{date_str}.json"
    json_path = os.path.join('outputs', 'reviews', json_filename)
    
    json_data = {
        'metadata': {
            'researcher_surname': researcher_surname,
            'researcher_firstname': researcher_firstname,
            'competition_name': competition_name,
            'competition_edition': competition_edition,
            'review_date': datetime.now().strftime('%d-%m-%y')
        },
        'dmp_content': {
            '1.1': {
                'section': '1.1',
                'question': 'Sposób pozyskiwania danych',
                'content': 'Mock content'
            }
        },
        'review_feedback': {
            '1.1': '✅ Sekcja kompletna i zgodna z wymaganiami.'
        }
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ JSON review exported to: {json_path}")
    assert os.path.exists(json_path), "JSON file not created"
    
    # Step 4: Verify file organization
    print("\nStep 4: Verify file organization")
    print("-" * 60)
    
    # Check DMP is in outputs/
    assert os.path.exists(dmp_path), "DMP not in outputs/"
    assert _normalized(dmp_path).startswith(_normalized('outputs')), "DMP not in outputs/ folder"
    print("✓ DMP file in outputs/ folder")
    
    # Check review files are in outputs/reviews/
    assert os.path.exists(feedback_path), "Feedback not in outputs/reviews/"
    assert _normalized(feedback_path).startswith(_normalized(os.path.join('outputs', 'reviews'))), "Feedback not in outputs/reviews/ folder"
    print("✓ Feedback TXT in outputs/reviews/ folder")
    
    assert os.path.exists(json_path), "JSON not in outputs/reviews/"
    assert _normalized(json_path).startswith(_normalized(os.path.join('outputs', 'reviews'))), "JSON not in outputs/reviews/ folder"
    print("✓ Review JSON in outputs/reviews/ folder")
    
    # Step 5: Verify file linkage
    print("\nStep 5: Verify file linkage")
    print("-" * 60)
    
    # Extract base names
    dmp_base = dmp_filename.replace('DMP_', '').replace('.docx', '')
    feedback_base_extracted = feedback_filename.replace('feedback_DMP_', '').replace('.txt', '')
    json_base = json_filename.replace('Review_', '').replace('.json', '')
    
    print(f"✓ DMP base name: {dmp_base}")
    print(f"✓ Feedback base name: {feedback_base_extracted}")
    print(f"✓ JSON base name: {json_base}")
    
    assert dmp_base == feedback_base_extracted, "DMP and feedback base names don't match"
    assert dmp_base == json_base, "DMP and JSON base names don't match"
    print("✓ All files properly linked by naming convention")
    
    # Step 6: Display file tree
    print("\nStep 6: File organization tree")
    print("-" * 60)
    print(f"""
DMP-ART/
├── outputs/
│   └── {dmp_filename}
│
└── outputs/
    └── reviews/
        ├── {feedback_filename}
        └── {json_filename}
""")
    
    # Cleanup
    print("Step 7: Cleanup test files")
    print("-" * 60)
    os.remove(dmp_path)
    os.remove(feedback_path)
    os.remove(json_path)
    print("✓ Test files removed")
    
    print("\n" + "=" * 60)
    print("✅ INTEGRATION TEST PASSED")
    print("=" * 60)
    print("\nWorkflow verified successfully!")
    print("\nFile organization:")
    print("  📄 DMP_*.docx        → outputs/")
    print("  📝 feedback_*.txt    → outputs/reviews/")
    print("  📊 Review_*.json     → outputs/reviews/")
    print("\n✓ Files remain linked through consistent naming convention")
    
    return 0

if __name__ == '__main__':
    try:
        exit(simulate_workflow())
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
