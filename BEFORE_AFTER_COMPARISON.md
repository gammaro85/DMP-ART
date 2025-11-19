# Before and After: Feedback Folder Separation

## Before Implementation

```
DMP-ART/
├── outputs/
│   ├── DMP_Kowalski_J_OPUS_29_191125.docx          ✓ DMP extraction
│   ├── feedback_DMP_Kowalski_J_OPUS_29_191125.txt  ← Feedback (wrong location)
│   ├── Review_Kowalski_J_OPUS_29_191125.json       ← Review JSON (wrong location)
│   └── cache_*.json
│
└── uploads/
    └── (temporary files)
```

**Issues:**
- ❌ DMP extractions and reviews mixed in same folder
- ❌ Hard to separate DMP files from review files
- ❌ Doesn't meet requirement #7: "DMP ma się zapisywać w jednym folderze, recenzja w drugim"

---

## After Implementation

```
DMP-ART/
├── outputs/                                         ← DMP files only
│   ├── DMP_Kowalski_J_OPUS_29_191125.docx          ✓ DMP extraction
│   ├── DMP_Nowak_A_PRELUDIUM_24_151125.docx        ✓ Another DMP
│   └── cache_*.json                                 ✓ Processing cache
│
├── feedback/                                        ← Review files only (NEW!)
│   ├── feedback_DMP_Kowalski_J_OPUS_29_191125.txt  ✓ Text feedback
│   ├── feedback_DMP_Nowak_A_PRELUDIUM_24_151125.txt ✓ Another feedback
│   ├── Review_Kowalski_J_OPUS_29_191125.json       ✓ JSON review
│   └── Review_Nowak_A_PRELUDIUM_24_151125.json     ✓ Another JSON review
│
└── uploads/
    └── (temporary files)
```

**Benefits:**
- ✅ Clear separation: DMPs in `outputs/`, reviews in `feedback/`
- ✅ Easy to find all DMPs or all reviews
- ✅ Meets requirement #7 perfectly
- ✅ Files remain linked by naming convention
- ✅ Better organization for data stewards

---

## File Linkage Examples

### Example 1: Kowalski's Application
```
DMP:      outputs/DMP_Kowalski_J_OPUS_29_191125.docx
Feedback: feedback/feedback_DMP_Kowalski_J_OPUS_29_191125.txt
JSON:     feedback/Review_Kowalski_J_OPUS_29_191125.json
          └────────┬────────┘
            Same base name: Kowalski_J_OPUS_29_191125
```

### Example 2: Nowak's Application
```
DMP:      outputs/DMP_Nowak_A_PRELUDIUM_24_151125.docx
Feedback: feedback/feedback_DMP_Nowak_A_PRELUDIUM_24_151125.txt
JSON:     feedback/Review_Nowak_A_PRELUDIUM_24_151125.json
          └────────┬────────┘
            Same base name: Nowak_A_PRELUDIUM_24_151125
```

---

## Finding Linked Files

### From DMP to Feedback
```bash
# Given DMP file: DMP_Kowalski_J_OPUS_29_191125.docx
# Find feedback:   feedback_DMP_Kowalski_J_OPUS_29_191125.txt

DMP_FILE="DMP_Kowalski_J_OPUS_29_191125.docx"
FEEDBACK_FILE="feedback_${DMP_FILE%.docx}.txt"
FEEDBACK_PATH="feedback/${FEEDBACK_FILE}"
```

### From DMP to JSON Review
```bash
# Given DMP file: DMP_Kowalski_J_OPUS_29_191125.docx
# Find review:    Review_Kowalski_J_OPUS_29_191125.json

DMP_FILE="DMP_Kowalski_J_OPUS_29_191125.docx"
BASE_NAME="${DMP_FILE#DMP_}"  # Remove "DMP_" prefix
BASE_NAME="${BASE_NAME%.docx}"  # Remove ".docx" extension
JSON_FILE="Review_${BASE_NAME}.json"
JSON_PATH="feedback/${JSON_FILE}"
```

### List All Pairs
```bash
# List all DMP files and their corresponding feedback files
for dmp in outputs/DMP_*.docx; do
    base=$(basename "$dmp" .docx)
    base="${base#DMP_}"
    
    feedback="feedback/feedback_DMP_${base}.txt"
    json="feedback/Review_${base}.json"
    
    echo "DMP:      $dmp"
    echo "Feedback: $feedback"
    echo "JSON:     $json"
    echo "---"
done
```

---

## Data Steward Workflow

### 1. Upload Proposal → Extract DMP
```
Input:  proposal.pdf (80 pages)
Output: outputs/DMP_Kowalski_J_OPUS_29_191125.docx (5 pages)
```

### 2. Review DMP → Create Feedback
```
Input:  outputs/DMP_Kowalski_J_OPUS_29_191125.docx
Action: Review all 14 sections, add comments
Output: feedback/feedback_DMP_Kowalski_J_OPUS_29_191125.txt
```

### 3. Export Structured Review
```
Input:  Review data from interface
Output: feedback/Review_Kowalski_J_OPUS_29_191125.json
```

### 4. Submit to Researcher
```
Attach: feedback/feedback_DMP_Kowalski_J_OPUS_29_191125.txt
        or
        feedback/Review_Kowalski_J_OPUS_29_191125.json
```

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Folder Structure** | 1 folder (outputs/) | 2 folders (outputs/, feedback/) |
| **File Separation** | ❌ Mixed DMP + reviews | ✅ Separated DMP vs reviews |
| **Organization** | ❌ Hard to find reviews | ✅ Easy to find everything |
| **Requirement #7** | ❌ Not met | ✅ Fully met |
| **File Linkage** | ✓ By naming | ✅ By naming (maintained) |
| **Data Steward UX** | ❌ Confusing | ✅ Clear and organized |

**Status**: ✅ **REQUIREMENT #7 FULLY IMPLEMENTED**
