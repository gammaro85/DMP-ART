"""
Diagnostic test for section 5.2 extraction issue.

User reports that section 5.2 content is being skipped.
This test will check if the anchor for 5.2 is being found correctly.
"""

import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

if __name__ != '__main__':
    raise unittest.SkipTest('Manual diagnostic script')

from utils.extractor_v2 import AnchorMatcher, TextBlock, normalize, token_overlap
import json

# Load anchor configuration
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'dmp_anchors.json')
with open(config_path, 'r', encoding='utf-8') as f:
    anchors_cfg = json.load(f)

# User's section 5 text
section_5_text = """
5. Udostępnianie i długotrwałe przechowywanie danych

Sposób i termin udostępnienia danych. Ewentualne ograniczenia w udostępnianiu danych lub przyczyny embarga

The data set will be shared via MOST Wiedzy Open Research Catalog. If needed the part of the data will be published in scientific journals, which may also require raw data publication. Data will be systematically uploaded to the MOST Wiedzy repository in accordance with the publication dates of the articles that are derived from this data.

Only new data, generated during this project, will be published in the MOST Wiedzy repository.

Sposób wyboru danych przeznaczonych do przechowania oraz miejsce długotrwałego przechowywania danych (np. repozytorium lub archiwum danych)

The MOST Wiedzy Open Research Data Catalog will be the main data repository. The repository is CoreTrustSeal certified, which means that it has established good preservation and dissemination practices The data provided in the repository will fulfill FAIR requirements. During the research team meetings will discuss the gathered data and will decide on what part of research data is worth being included in repository and whether it is self-explanatory in its current form or will need an additional processing. Moreover, all data will be stored for at least 10 years after the project is finished and access to them will be possible only with the PI consent.

Metody lub narzędzia programowe umożliwiające dostęp do danych i korzystanie z danych

The shared data will be in open formats, so there will be no need for specialized software by recipients.

Sposób zapewniający stosowanie unikalnego i trwałego identyfikatora (np. cyfrowego identyfikatora obiektu (DOI)) dla każdego zestawu danych

The datasets provided in the repository will have the DOI assigned.
"""

# Convert to TextBlocks (simulate PDF/DOCX conversion)
lines = section_5_text.strip().split('\n')
blocks = []
for i, line in enumerate(lines):
    text = line.strip()
    if text:
        blocks.append(TextBlock(text, False, False, 'paragraph', 0, False))

print(f"Created {len(blocks)} text blocks")
print("\n" + "="*80)
print("BLOCK LIST:")
print("="*80)
for i, blk in enumerate(blocks):
    print(f"{i:3d}: {blk.text[:100]}")

# Test anchor matching for sections 5.1, 5.2, 5.3, 5.4
print("\n" + "="*80)
print("ANCHOR MATCHING TEST")
print("="*80)

matcher = AnchorMatcher(anchors_cfg.get('sections', {}))

# Test each section individually
for section_id in ['5.1', '5.2', '5.3', '5.4']:
    cfg = anchors_cfg['sections'][section_id]
    anchor_texts = cfg.get('pl', []) + cfg.get('en', [])
    fingerprint = cfg.get('fingerprint_pl', []) + cfg.get('fingerprint_en', [])

    print(f"\n{'='*80}")
    print(f"SECTION {section_id}")
    print(f"{'='*80}")
    print(f"Polish anchors:")
    for txt in cfg.get('pl', []):
        print(f"  - {txt}")
    print(f"English anchors:")
    for txt in cfg.get('en', []):
        print(f"  - {txt}")
    print(f"Fingerprint keywords: {fingerprint}")

    # Find matches
    idx, win_size, score = matcher._locate(blocks, anchor_texts, fingerprint)

    if idx >= 0:
        print(f"\n[FOUND] at block {idx} (window={win_size}, score={score:.3f})")
        print(f"Matched blocks:")
        for i in range(idx, min(idx + win_size, len(blocks))):
            print(f"  {i}: {blocks[i].text}")
    else:
        print(f"\n[NOT FOUND]")

        # Debug: show best matches for each block
        print(f"\nDEBUG: Best token overlap scores per block:")
        norm_anchors = [normalize(a) for a in anchor_texts]
        for i, blk in enumerate(blocks):
            norm_blk = normalize(blk.text)
            best_score = max(
                (token_overlap(na, norm_blk) for na in norm_anchors),
                default=0.0
            )
            if best_score > 0.1:  # Only show potentially relevant blocks
                print(f"  Block {i:3d} (score={best_score:.3f}): {blk.text[:80]}")

# Now test full boundary finding (forward search)
print("\n" + "="*80)
print("FULL BOUNDARY DETECTION (forward search)")
print("="*80)

from utils.extractor_v2 import SECTION_ORDER
boundaries = matcher.find_boundaries(blocks)

print(f"\nFound {len(boundaries)} boundaries:")
for sid in SECTION_ORDER:
    if sid in boundaries:
        start_idx, win_size = boundaries[sid]
        print(f"  {sid}: blocks {start_idx}-{start_idx+win_size-1} (window={win_size})")
        print(f"       Text: {blocks[start_idx].text[:80]}")
    elif sid.startswith('5'):  # Only show section 5 subsections
        print(f"  {sid}: NOT FOUND")

# Simulate content extraction
print("\n" + "="*80)
print("CONTENT EXTRACTION SIMULATION")
print("="*80)

if boundaries:
    ordered = sorted(boundaries.items(), key=lambda x: x[1][0])
    for rank, (sid, (start_idx, win_size)) in enumerate(ordered):
        content_start = start_idx + win_size
        if rank + 1 < len(ordered):
            next_start_idx, _ = ordered[rank + 1][1]
            content_end = next_start_idx
        else:
            content_end = len(blocks)

        content_blocks = blocks[content_start:content_end]
        print(f"\nSection {sid}:")
        print(f"  Anchor: blocks {start_idx}-{start_idx+win_size-1}")
        print(f"  Content: blocks {content_start}-{content_end-1} ({len(content_blocks)} blocks)")
        if content_blocks:
            print(f"  First content block: {content_blocks[0].text[:80]}")
            print(f"  Last content block: {content_blocks[-1].text[:80]}")
        else:
            print(f"  [WARNING] NO CONTENT BLOCKS!")
