# Extractor v3 Integration — Separated Slicing & Cleaning

**Status:** ✅ Implemented & Integrated  
**Date:** 2026-05-28  
**Branch:** (current)

---

## 📋 Summary

Zaimplementowano eksperymentalny **extractor v3** z separacją faz slicing i cleaning, dostępny jako tryb debugowania w aplikacji DMP-ART.

### Kluczowe różnice: v2 vs v3

| Aspekt | v2 (Production) | v3 (Debug) |
|--------|----------------|------------|
| **Pipeline** | Slice → Clean (per-section) | Slice ALL → Clean ALL |
| **Wynik** | ✅ Identyczny | ✅ Identyczny |
| **RAW data export** | ❌ Nie | ✅ Tak (opcjonalne) |
| **Cache size** | Bazowy | +20-30% (z RAW) |
| **Separacja kodu** | Cleaner w Extractorze | Niezależne moduły |
| **Testowanie** | Razem | Osobno |

---

## 🎯 Cel implementacji

1. **Lepsze debugowanie** - możliwość inspekcji surowych slice'ów przed cleaningiem
2. **Separation of concerns** - niezależne moduły łatwiejsze do testowania
3. **Analiza problemów** - porównanie RAW vs CLEANED content
4. **Eksperymentowanie** - łatwiejsze testowanie nowych strategii cleaningu

---

## 📁 Nowe pliki

### 1. `utils/extractor_v3_separated.py`

Główna implementacja v3 z separacją faz:

```python
from utils.extractor_v3_separated import DMPExtractorSeparated

# Produkcja (bez RAW data)
extractor = DMPExtractorSeparated(save_raw_slices=False)

# Debug (z RAW data)
extractor = DMPExtractorSeparated(save_raw_slices=True)

result = extractor.process_file(file_path, output_dir)
```

**Pipeline:**
1. `DocConverter` → TextBlocks
2. `AnchorMatcher` → boundaries
3. `_slice_sections()` → raw sections (Dict[section_id, List[TextBlock]])
4. `_clean_sections()` → cleaned sections (Dict[section_id, List[str]])
5. `_build_cache()` → final cache (z opcjonalnym RAW)

### 2. `tests/test_v2_vs_v3_comparison.py`

Test porównawczy weryfikujący identyczność wyników:

```bash
python tests/test_v2_vs_v3_comparison.py <path_to_dmp.docx>
```

**Wyniki testu:**
```
[OK] ALL SECTIONS MATCH - Cleaning produces identical results!
[OK] V3 exported 3 raw sections for debugging
Cache size: v2=4,831 bytes, v3=5,915 bytes (+22.4%)
```

### 3. Integracja w `app.py`

**Nowe zmienne globalne:**
```python
DEBUG_MODE = False  # Loaded from config/settings.json
```

**Automatyczny wybór ekstraktora:**
```python
if DEBUG_MODE:
    extractor = DMPExtractorSeparated(save_raw_slices=True)  # v3
else:
    extractor = DMPExtractor()  # v2 (default)
```

**Nowe API endpoints:**
- `GET /api/settings/extractor-debug` - pobierz status
- `POST /api/settings/extractor-debug` - przełącz v2/v3

---

## 🎨 UI Controls (Settings Page)

Nowa sekcja **"Extractor Debug Mode"** w Settings → General:

```
┌─────────────────────────────────────────┐
│ 🐛 Extractor Debug Mode                 │
├─────────────────────────────────────────┤
│ ☐ Enable v3 Extractor (Debug Mode)      │
│                                          │
│ v2 (Production): Optimized extraction   │
│ v3 (Debug): RAW data export for debug   │
│                                          │
│ Current: v2-production                   │
└─────────────────────────────────────────┘
```

**Funkcje JavaScript:**
- `toggleExtractorDebug(enabled)` - przełącz tryb
- `loadExtractorDebugStatus()` - załaduj status

---

## 💾 Struktura cache v3 (z save_raw_slices=True)

```json
{
  "1.1": {
    "section": "1. Data description...",
    "question": "How will new data...",
    "paragraphs": [                    // ← CLEANED (identyczne jak v2)
      "Data will be collected through interviews",
      "Approximately 60 interviews will be conducted"
    ],
    "tagged_paragraphs": [...],
    "raw_blocks": [                    // ← RAW (NOWE w v3!)
      "1.1 How will new data be collected?",
      "",
      "Data will be collected through interviews",
      "Approximately 60 interviews will be conducted"
    ]
  },
  "_unconnected_text": [...],
  "_raw_sections": {                   // ← Globalna kolekcja RAW (NOWE!)
    "1.1": ["raw", "blocks", "with", "numerations"],
    "1.2": [...]
  }
}
```

**Dodatkowe pola tylko w v3:**
- `raw_blocks` - surowe bloki per sekcja (z numeracjami, pytaniami)
- `_raw_sections` - wszystkie surowe sekcje (debug dump)

---

## 🔧 Użycie

### Przełączanie przez UI (Recommended)

1. Otwórz aplikację: `http://localhost:5000`
2. Przejdź do: **Settings → General**
3. Przewiń do sekcji: **"Extractor Debug Mode"**
4. Zaznacz: **☑ Enable v3 Extractor (Debug Mode)**
5. Status zmieni się na: `v3-separated`

**Zmiana jest trwała** - zapisywana w `config/settings.json`.

### Przełączanie przez API

```bash
# Włącz v3 (debug)
curl -X POST http://localhost:5000/api/settings/extractor-debug \
  -H "Content-Type: application/json" \
  -d '{"debug_mode": true}'

# Wyłącz v3 (powrót do v2)
curl -X POST http://localhost:5000/api/settings/extractor-debug \
  -H "Content-Type: application/json" \
  -d '{"debug_mode": false}'

# Sprawdź status
curl http://localhost:5000/api/settings/extractor-debug
```

### Programatyczne użycie (bez app.py)

```python
# Tylko v3 (standalone)
from utils.extractor_v3_separated import DMPExtractorSeparated

extractor = DMPExtractorSeparated(save_raw_slices=True)
result = extractor.process_file('test.pdf', 'outputs')

if result['success']:
    cache_path = f"outputs/cache/cache_{result['cache_id']}.json"
    # Cache zawiera raw_blocks i _raw_sections
```

---

## 📊 Test Results

### Porównanie na prawdziwym DMP

**Plik testowy:** `tests/fixtures/test_dmp_simple.docx` (3 sekcje wypełnione)

```
================================================================================
COMPARISON: extractor_v2 vs extractor_v3_separated
================================================================================

1. CLEANED PARAGRAPHS (should be identical):
--------------------------------------------------------------------------------
1.1: [OK] MATCH (v2: 0 lines, v3: 0 lines)
1.2: [OK] MATCH (v2: 6 lines, v3: 6 lines)
2.1: [OK] MATCH (v2: 5 lines, v3: 5 lines)
2.2: [OK] MATCH (v2: 2 lines, v3: 2 lines)
3.1: [OK] MATCH (v2: 0 lines, v3: 0 lines)
... (all sections match)

[OK] ALL SECTIONS MATCH - Cleaning produces identical results!

2. V3 RAW SLICES (debugging feature):
--------------------------------------------------------------------------------
[OK] V3 exported 3 raw sections for debugging
[OK] V3 includes raw_blocks in 3 sections

4. CACHE SIZE COMPARISON:
--------------------------------------------------------------------------------
V2 cache size: 4,831 bytes
V3 cache size: 5,915 bytes (with raw data)
Difference: +1,084 bytes (22.4% larger)
```

**✅ Wnioski:**
- Cleaning produces **identyczne wyniki** w obu wersjach
- v3 dodaje ~22% do rozmiaru cache (tylko z `save_raw_slices=True`)
- RAW data jest dostępna tylko w v3

---

## 🐛 Debugging workflow (przykład)

### Problem: Sekcja 1.1 jest pusta po ekstrakcji

**Krok 1: Włącz v3 debug mode**
```
Settings → General → ☑ Enable v3 Extractor
```

**Krok 2: Przetwórz plik ponownie**
```
Upload DMP → Ekstrahuj
```

**Krok 3: Sprawdź RAW cache**
```json
// outputs/cache/cache_xxx.json
{
  "1.1": {
    "paragraphs": [],           // ← CLEANED (puste!)
    "raw_blocks": [              // ← RAW (sprawdź co było PRZED cleaningiem)
      "1.1 Jakie dane będą zebrane lub wytworzone?",
      "",
      "DANE BADAWCZE",           // ← To zostało odfiltrowane!
      "Projekt obejmuje..."
    ]
  }
}
```

**Krok 4: Zidentyfikuj problem**
- ContentCleaner usunął "DANE BADAWCZE" jako skip term
- Możliwe przyczyny:
  1. User skip term: `config/extraction_skip_terms.json`
  2. Builtin noise: `_BUILTIN_NOISE` regex w `extractor_v2.py`

**Krok 5: Fix**
- Usuń "DANE BADAWCZE" z skip terms
- LUB zmodyfikuj regex w `_BUILTIN_NOISE`

**Krok 6: Wyłącz v3 (produkcja)**
```
Settings → General → ☐ Disable v3 Extractor
```

---

## ⚠️ Trade-offs

### Zalety v3 (Debug Mode)

✅ **Debugging** - RAW slices pokazują co zostało odfiltrowane  
✅ **Testowanie** - niezależne unit testy slicingu i cleaningu  
✅ **Separacja** - cleaner jest osobnym modułem  
✅ **Batch processing** - możliwość optymalizacji w przyszłości  

### Wady v3 (Debug Mode)

❌ **Pamięć** - wszystkie RAW slices trzymane do końca (~22% większy cache)  
❌ **Złożoność** - więcej kroków w pipeline  
❌ **Performance** - minimalnie wolniejszy (przez dodatkowy krok)  

---

## 🚀 Rekomendacje użycia

### Użyj v2 (Production) gdy:
- ✅ Normalny workflow produkcyjny
- ✅ Optymalizacja pamięci jest ważna
- ✅ Cache musi być minimalny
- ✅ Ekstrakcja działa poprawnie

### Użyj v3 (Debug) gdy:
- ✅ Debugujesz problemy ekstrakcji
- ✅ Porównujesz RAW vs CLEANED content
- ✅ Testujesz nowe skip terms
- ✅ Analizujesz dlaczego sekcja jest pusta
- ✅ Rozwijasz nowe featury extractora

---

## 📝 Konfiguracja (config/settings.json)

```json
{
  "max_upload_mb": 16,
  "extractor_debug_mode": false    // ← false=v2, true=v3
}
```

**Zmiana przez UI automatycznie zapisuje do tego pliku.**

---

## 🔄 Compatibility

### Backward compatibility

✅ **v3 produkuje identyczne `paragraphs` jak v2**  
✅ **review.html działa z oboma wersjami cache**  
✅ **Można przełączać między v2/v3 bez restartu app**  
✅ **Stare cache (v2) są kompatybilne**  

### Forward compatibility

⚠️ **Cache v3 (z RAW) ma dodatkowe pola** (`raw_blocks`, `_raw_sections`)  
✅ **review.html ignoruje te pola** (nie są renderowane)  
✅ **Stary kod może otworzyć cache v3** (pomija nieznane pola)

---

## 📚 Pliki zmodyfikowane

```
app.py                                    # Import v3, wybór ekstraktora, API endpoints
templates/settings.html                    # UI controls, JavaScript functions
utils/extractor_v3_separated.py           # NOWY: v3 implementation
tests/test_v2_vs_v3_comparison.py         # NOWY: test porównawczy
tests/create_test_dmp.py                  # NOWY: generator testowego DMP
tests/fixtures/test_dmp_simple.docx       # NOWY: plik testowy
EXTRACTOR_V3_INTEGRATION.md               # NOWY: ta dokumentacja
```

---

## ✅ Verification Checklist

- [x] v3 extractor implementowany (`extractor_v3_separated.py`)
- [x] Test porównawczy przechodzi (`test_v2_vs_v3_comparison.py`)
- [x] Integracja w `app.py` działa
- [x] API endpoints działają
- [x] UI controls w Settings działają
- [x] Persistence w `config/settings.json` działa
- [x] Cache v3 zawiera RAW data gdy `save_raw_slices=True`
- [x] review.html renderuje oba formaty cache
- [x] Backward compatibility zachowana

---

## 🎓 Lessons Learned

1. **Separacja kodu ≠ zmiana wyników** - oba ekstraktory produkują identyczne cleaned content
2. **RAW data export ma koszt** - +22% cache size, ale bezcenny przy debugowaniu
3. **Modułowa architektura ułatwia testowanie** - slice i clean można testować osobno
4. **UI toggle jest lepsze niż env var** - użytkownik może łatwo eksperymentować

---

**Koniec dokumentacji**  
Pytania? Zobacz: `tests/test_v2_vs_v3_comparison.py` lub uruchom aplikację i sprawdź Settings → General.
