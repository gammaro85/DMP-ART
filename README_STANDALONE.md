# DMP-ART Standalone - Quick Start Guide

## 🚀 Szybki Start (Quick Start)

### Krok 1: Rozpakuj archiwum
```
Rozpakuj DMP-ART-Standalone.zip do wybranego folderu
```

### Krok 2: Uruchom aplikację
- **Windows:** Kliknij dwukrotnie `DMP-ART.exe`
- **Linux/Mac:** Terminal → `./DMP-ART`

### Krok 3: Pracuj!
- Przeglądarka otworzy się automatycznie na `http://localhost:5000`
- Wrzuć pliki PDF/DOCX do folderu `input/`
- Prześlij przez interfejs webowy i zacznij recenzję

---

## 📁 Struktura Folderów (Folder Structure)

```
DMP-ART/
│
├── DMP-ART.exe          ← URUCHOM TEN PLIK (RUN THIS FILE)
├── _internal/           ← Python runtime (nie ruszać!)
│
├── input/               ← WRZUĆ TU PLIKI PDF/DOCX
│   └── README.txt       ← Instrukcje dla folderu input
│
├── output/              ← TUTAJ ZAPISUJĄ SIĘ WYNIKI
│   ├── dmp/             ← Wyekstrahowane DMPy
│   ├── reviews/         ← Twoje recenzje
│   └── cache/           ← Cache (można usuwać)
│   └── README.txt       ← Instrukcje dla folderu output
│
├── config/              ← SZABLONY KOMENTARZY (edytowalne!)
│   ├── quick_comments.json
│   ├── newcomer.json
│   ├── mising.json
│   └── ready.json
│
└── INSTRUKCJA.txt       ← PEŁNA POLSKA INSTRUKCJA
```

---

## ⚡ Najczęstsze Pytania (FAQ)

### ❓ Jak używać aplikacji?

1. **Uruchom** `DMP-ART.exe`
2. **Otwórz** http://localhost:5000 (otworzy się automatycznie)
3. **Prześlij** plik PDF/DOCX z wnioskiem NCN
4. **Recenzuj** - aplikacja podzieli DMP na 14 sekcji
5. **Zapisz** feedback klikając "Zapisz feedback"
6. **Eksportuj** do pliku tekstowego

### ❓ Czy muszę coś instalować?

**NIE!** To jest wersja standalone - wszystko jest w środku.

**Wyjątek:** Dla skanów PDF (OCR) musisz zainstalować Tesseract OCR:
- Windows: https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr tesseract-ocr-pol`
- Mac: `brew install tesseract`

### ❓ Gdzie są moje pliki?

- **Przesłane:** `input/` lub tymczasowo w `uploads/`
- **Wyekstrahowane DMPy:** `output/dmp/`
- **Zapisane recenzje:** `output/reviews/`

### ❓ Jak edytować szybkie komentarze?

1. Otwórz folder `config/`
2. Edytuj pliki JSON w Notatniku
3. Zapisz zmiany
4. Uruchom ponownie aplikację

### ❓ Aplikacja nie uruchamia się - co robić?

**Sprawdź:**
- Czy port 5000 jest wolny (zamknij inne aplikacje)
- Czy antywirus nie blokuje (dodaj do wyjątków)
- Uruchom jako Administrator (Windows)

**Otwórz ręcznie przeglądarkę:**
- Jeśli aplikacja się uruchomiła ale przeglądarka nie, wejdź na: http://localhost:5000

### ❓ Jak zatrzymać aplikację?

- Zamknij okno konsoli (czarne okno), LUB
- Naciśnij `Ctrl+C` w konsoli

---

## 🔧 Wymagania Systemowe (System Requirements)

### Minimalne:
- **OS:** Windows 10, Ubuntu 20.04, macOS 11
- **RAM:** 2 GB
- **Dysk:** 500 MB wolnego miejsca
- **Przeglądarka:** Chrome, Firefox, Edge (nowoczesne wersje)

### Zalecane:
- **RAM:** 4 GB
- **Dysk:** 2 GB (dla cache i plików roboczych)

---

## 📊 Obsługiwane Formaty (Supported Formats)

✅ **PDF** - Normalne (z tekstem) i skany (OCR wymagany)
✅ **DOCX** - Microsoft Word 2007+

**Maksymalny rozmiar:** 16 MB

---

## ⚠️ Ograniczenia (Limitations)

- **Tylko jeden użytkownik** - aplikacja nie obsługuje wielu użytkowników jednocześnie
- **Tylko lokalne** - działa tylko na Twoim komputerze (nie ma dostępu z sieci)
- **OCR wymaga Tesseract** - skany PDF wymagają osobnej instalacji Tesseract
- **Eksport tylko TXT** - na razie eksport do DOCX/PDF jest w planach

---

## 🐛 Zgłaszanie Błędów (Bug Reports)

Znalazłeś błąd? Masz sugestie?

**Zgłoś problem:**
https://github.com/gammaro85/DMP-ART/issues

**Podaj:**
- System operacyjny i wersję
- Dokładny opis problemu
- Komunikat błędu (jeśli jest)
- Kroki do odtworzenia

---

## 📚 Więcej Informacji (More Information)

- **Pełna instrukcja:** Zobacz `INSTRUKCJA.txt` w tym folderze
- **Dokumentacja projektu:** https://github.com/gammaro85/DMP-ART
- **Build guide:** https://github.com/gammaro85/DMP-ART/blob/main/BUILD.md

---

## ⚖️ Licencja (License)

DMP-ART jest oprogramowaniem open-source na licencji MIT.

Copyright (c) 2024 gammaro85

---

## 🙏 Podziękowania (Credits)

**Używane biblioteki:**
- Flask - Web framework
- PyPDF2 - PDF processing
- python-docx - DOCX processing
- Pillow - Image processing
- Tesseract OCR - Optical character recognition

---

**Wersja:** 0.8.1 Standalone
**Data buildu:** 2024-12-03
**Autor:** gammaro85

---

### 🎉 Dziękujemy za używanie DMP-ART!

Masz pytania? Zobacz `INSTRUKCJA.txt` lub odwiedź:
https://github.com/gammaro85/DMP-ART

