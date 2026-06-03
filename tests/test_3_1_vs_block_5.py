"""
Debug why 3.1 anchor matches block 5 (which is actually 5.2 content).
"""

import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

if __name__ != '__main__':
    raise unittest.SkipTest('Manual diagnostic script')

from utils.extractor_v2 import normalize, token_overlap
import json

# Load anchor configuration
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'dmp_anchors.json')
with open(config_path, 'r', encoding='utf-8') as f:
    anchors_cfg = json.load(f)

# Block 5 from user's text (answer to 5.2)
block_5_text = """The MOST Wiedzy Open Research Data Catalog will be the main data repository. The repository is CoreTrustSeal certified, which means that it has established good preservation and dissemination practices The data provided in the repository will fulfill FAIR requirements. During the research team meetings will discuss the gathered data and will decide on what part of research data is worth being included in repository and whether it is self-explanatory in its current form or will need an additional processing. Moreover, all data will be stored for at least 10 years after the project is finished and access to them will be possible only with the PI consent."""

# Get 3.1 anchors
cfg_3_1 = anchors_cfg['sections']['3.1']
anchors_3_1 = cfg_3_1.get('pl', []) + cfg_3_1.get('en', [])

print("3.1 ANCHOR TEXTS:")
print("="*80)
for i, anchor in enumerate(anchors_3_1):
    print(f"{i+1}. {anchor}")

print("\n\nBLOCK 5 TEXT:")
print("="*80)
print(block_5_text)

print("\n\nTOKEN OVERLAP SCORES:")
print("="*80)
norm_block = normalize(block_5_text)
print(f"Normalized block 5: {norm_block[:200]}...")

for i, anchor in enumerate(anchors_3_1):
    norm_anchor = normalize(anchor)
    score = token_overlap(norm_anchor, norm_block)
    print(f"\nAnchor {i+1} score: {score:.3f}")
    print(f"  Anchor: {norm_anchor}")

    # Show which tokens match
    anchor_tokens = set(norm_anchor.split())
    block_tokens = set(norm_block.split())
    matched = anchor_tokens & block_tokens
    print(f"  Matched tokens ({len(matched)}/{len(anchor_tokens)}): {sorted(matched)}")
    if score >= 0.20:  # MIN_FIRST_BLOCK threshold
        print(f"  ⚠️ SCORE >= 0.20 (MIN_FIRST_BLOCK) - this block would be considered!")

# Also check 5.2 anchors
print("\n\n5.2 ANCHOR MATCH (for comparison):")
print("="*80)
cfg_5_2 = anchors_cfg['sections']['5.2']
anchors_5_2 = cfg_5_2.get('pl', []) + cfg_5_2.get('en', [])

for i, anchor in enumerate(anchors_5_2):
    norm_anchor = normalize(anchor)
    score = token_overlap(norm_anchor, norm_block)
    print(f"\n5.2 Anchor {i+1} score: {score:.3f}")
    print(f"  Anchor: {norm_anchor}")
    anchor_tokens = set(norm_anchor.split())
    block_tokens = set(norm_block.split())
    matched = anchor_tokens & block_tokens
    print(f"  Matched tokens ({len(matched)}/{len(anchor_tokens)}): {sorted(matched)}")
