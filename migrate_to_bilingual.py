#!/usr/bin/env python3
"""
Migration Script: Convert existing comment JSON files to bilingual format

Converts:
- Category comments from string arrays to {en, pl} objects
- Quick comments from "text": string to "text": {en, pl}

Creates backups of original files before migration.
"""

import json
import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create timestamped backup of file"""
    backup_path = filepath.replace('.json', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def migrate_category_file(filepath):
    """Migrate category file from string array to bilingual object array"""
    print(f"\n🔄 Processing: {filepath}")

    # Create backup
    backup_file(filepath)

    # Load current structure
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Get category name (first key that doesn't start with underscore)
    category_name = None
    for key in data.keys():
        if not key.startswith('_') and isinstance(data[key], dict):
            category_name = key
            break

    if not category_name:
        print(f"⚠️  No valid category found in {filepath}")
        return 0

    category_data = data[category_name]

    # Track changes
    total_comments = 0
    migrated_comments = 0

    # Migrate each section
    for section_id, comments in category_data.items():
        total_comments += len(comments)

        # Check if already migrated
        if comments and isinstance(comments[0], dict):
            print(f"  ⏭️  Section {section_id}: Already in bilingual format")
            continue

        # Convert string array to object array
        new_comments = []
        for comment in comments:
            new_comments.append({
                "en": comment,
                "pl": comment  # Initially same as English
            })
            migrated_comments += 1

        category_data[section_id] = new_comments
        print(f"  ✅ Section {section_id}: Migrated {len(new_comments)} comments")

    # Save migrated structure
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Migration complete: {migrated_comments}/{total_comments} comments converted")
    return migrated_comments

def migrate_quick_comments(filepath):
    """Migrate quick_comments.json from text: string to text: {en, pl}"""
    print(f"\n🔄 Processing: {filepath}")

    # Create backup
    backup_file(filepath)

    # Load current structure
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    quick_comments = data.get('quick_comments', [])

    # Track changes
    total_comments = len(quick_comments)
    migrated_comments = 0

    # Migrate each comment
    for comment in quick_comments:
        # Check if already migrated
        if isinstance(comment.get('text'), dict):
            print(f"  ⏭️  '{comment['name']}': Already in bilingual format")
            continue

        # Convert text: string to text: {en, pl}
        original_text = comment['text']
        comment['text'] = {
            "en": original_text,
            "pl": original_text  # Initially same as English
        }
        migrated_comments += 1
        print(f"  ✅ '{comment['name']}': Migrated")

    # Save migrated structure
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Migration complete: {migrated_comments}/{total_comments} comments converted")
    return migrated_comments

def main():
    """Main migration workflow"""
    print("="*80)
    print("DMP-ART: Comment Structure Migration to Bilingual Format")
    print("="*80)

    config_dir = 'config'

    # List of category files to migrate
    category_files = [
        'newcomer.json',
        'mising.json',  # Note: typo in original filename
        'ready.json'
    ]

    # List of other files to migrate
    other_files = [
        'quick_comments.json'
    ]

    total_migrated = 0

    # Migrate category files
    print("\n📁 CATEGORY FILES")
    print("-" * 80)
    for filename in category_files:
        filepath = os.path.join(config_dir, filename)
        if os.path.exists(filepath):
            count = migrate_category_file(filepath)
            total_migrated += count
        else:
            print(f"⚠️  File not found: {filepath}")

    # Migrate quick comments
    print("\n📁 QUICK COMMENTS")
    print("-" * 80)
    for filename in other_files:
        filepath = os.path.join(config_dir, filename)
        if os.path.exists(filepath):
            count = migrate_quick_comments(filepath)
            total_migrated += count
        else:
            print(f"⚠️  File not found: {filepath}")

    # Summary
    print("\n" + "="*80)
    print("MIGRATION SUMMARY")
    print("="*80)
    print(f"✅ Total comments migrated: {total_migrated}")
    print(f"✅ Backups created in: {config_dir}/")
    print(f"✅ All files now support bilingual comments (EN/PL)")
    print("\nℹ️  NOTE: Polish translations are currently identical to English.")
    print("   Use the Template Editor to add Polish translations.")
    print("="*80)

    # Verification
    print("\n🔍 VERIFICATION")
    print("-" * 80)

    # Check one file to verify structure
    test_file = os.path.join(config_dir, 'quick_comments.json')
    if os.path.exists(test_file):
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if data['quick_comments'] and isinstance(data['quick_comments'][0].get('text'), dict):
            print("✅ Verification passed: Bilingual structure confirmed")
            print(f"   Sample: {data['quick_comments'][0]['name']}")
            print(f"   - EN: {data['quick_comments'][0]['text']['en'][:50]}...")
            print(f"   - PL: {data['quick_comments'][0]['text']['pl'][:50]}...")
        else:
            print("⚠️  Verification warning: Structure may not be correct")

    print("\n✅ Migration complete! Ready for Phase 4 frontend implementation.")

if __name__ == '__main__':
    main()
