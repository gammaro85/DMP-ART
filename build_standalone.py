#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script for DMP-ART Standalone Distribution

Automatyzuje proces:
1. Budowanie executable z PyInstaller
2. Tworzenie struktury folderów (input/output/config)
3. Kopiowanie dokumentacji
4. Pakowanie do ZIP

Usage:
    python build_standalone.py
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
import subprocess
import io

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Kolory dla termianla
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_step(message, color=Colors.BLUE):
    """Wyświetla kolorowy komunikat kroku."""
    print(f"\n{color}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{color}{Colors.BOLD}{message}{Colors.END}")
    print(f"{color}{Colors.BOLD}{'='*60}{Colors.END}\n")

def run_command(command, description):
    """Uruchamia komendę shell z obsługą błędów."""
    print(f"▶ {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"{Colors.GREEN}✓ {description} - SUCCESS{Colors.END}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}✗ {description} - FAILED{Colors.END}")
        print(f"{Colors.RED}Error: {e.stderr}{Colors.END}")
        return False

def clean_previous_builds():
    """Usuwa poprzednie buildy."""
    print_step("🧹 Czyszczenie poprzednich buildów", Colors.YELLOW)

    folders_to_clean = ['build', 'dist']
    for folder in folders_to_clean:
        if os.path.exists(folder):
            print(f"▶ Usuwanie {folder}/...")
            try:
                shutil.rmtree(folder)
                print(f"{Colors.GREEN}✓ Usunięto {folder}/{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}✗ Błąd przy usuwaniu {folder}: {e}{Colors.END}")
                return False

    return True

def build_executable():
    """Buduje executable z PyInstaller."""
    print_step("🔨 Budowanie executable z PyInstaller", Colors.BLUE)

    # Sprawdzenie czy PyInstaller jest zainstalowany
    try:
        import PyInstaller
    except ImportError:
        print(f"{Colors.RED}✗ PyInstaller nie jest zainstalowany!{Colors.END}")
        print(f"{Colors.YELLOW}Instaluję: pip install pyinstaller{Colors.END}")
        if not run_command("pip install pyinstaller", "Instalacja PyInstaller"):
            return False

    # Budowanie
    if not run_command("pyinstaller DMP-ART.spec --clean", "PyInstaller build"):
        return False

    return True

def create_distribution_structure():
    """Tworzy pełną strukturę dystrybucji."""
    print_step("📁 Tworzenie struktury dystrybucji", Colors.BLUE)

    dist_path = Path('dist/DMP-ART')

    if not dist_path.exists():
        print(f"{Colors.RED}✗ Folder dist/DMP-ART nie istnieje! Build failed.{Colors.END}")
        return False

    # Struktura folderów
    folders = {
        'input': "📥 Folder na pliki PDF/DOCX do przetworzenia",
        'output': "📤 Folder na wyniki",
        'output/dmp': "📄 Wyekstrahowane plany DMP",
        'output/reviews': "✍️ Zapisane recenzje",
        'output/cache': "💾 Cache (można bezpiecznie usuwać)",
        'config': "⚙️ Szablony komentarzy i konfiguracja",
    }

    for folder, description in folders.items():
        folder_path = dist_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"{Colors.GREEN}✓ {folder}/{Colors.END} - {description}")

    return True

def copy_config_files():
    """Kopiuje pliki konfiguracyjne do dystrybucji."""
    print_step("⚙️ Kopiowanie plików konfiguracyjnych", Colors.BLUE)

    dist_path = Path('dist/DMP-ART')
    config_files = [
        'config/dmp_structure.json',
        'config/quick_comments.json',
        'config/newcomer.json',
        'config/mising.json',
        'config/ready.json',
    ]

    for config_file in config_files:
        if os.path.exists(config_file):
            dest = dist_path / config_file
            shutil.copy2(config_file, dest)
            print(f"{Colors.GREEN}✓ Skopiowano: {config_file}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠ Plik nie istnieje: {config_file}{Colors.END}")

    return True

def create_readme_files():
    """Tworzy pliki README w folderach."""
    print_step("📝 Tworzenie plików README", Colors.BLUE)

    dist_path = Path('dist/DMP-ART')

    # README dla folderu input
    input_readme = dist_path / 'input' / 'README.txt'
    input_readme.write_text("""
╔═══════════════════════════════════════════════════════════════╗
║                   FOLDER INPUT - INSTRUKCJA                   ║
╚═══════════════════════════════════════════════════════════════╝

📥 Ten folder służy do przechowywania plików PDF/DOCX z wnioskami NCN.

💡 JAK UŻYWAĆ:
1. Skopiuj tutaj pliki PDF lub DOCX z wnioskami do recenzji
2. Uruchom DMP-ART.exe (główny plik w folderze wyżej)
3. W aplikacji kliknij "Wybierz plik" i znajdź swój dokument
4. Prześlij i zacznij recenzję!

⚠️ UWAGA:
- Obsługiwane formaty: PDF, DOCX
- Maksymalny rozmiar pliku: 16 MB
- Pliki ze skanów (OCR) są automatycznie rozpoznawane

📤 Wyniki recenzji zapisują się w folderze "output/"
""", encoding='utf-8')

    # README dla folderu output
    output_readme = dist_path / 'output' / 'README.txt'
    output_readme.write_text("""
╔═══════════════════════════════════════════════════════════════╗
║                  FOLDER OUTPUT - STRUKTURA                    ║
╚═══════════════════════════════════════════════════════════════╝

📤 Ten folder zawiera wszystkie wyniki pracy aplikacji DMP-ART.

📁 STRUKTURA:
├── dmp/       - Wyekstrahowane sekcje DMP (podzielone na 14 części)
├── reviews/   - Zapisane recenzje z Twoimi komentarzami
└── cache/     - Pliki cache (można bezpiecznie usuwać)

💾 CACHE:
Folder "cache/" zawiera tymczasowe pliki JSON przyspieszające pracę.
Można go bezpiecznie usunąć - aplikacja odtworzy cache przy następnym użyciu.

🗑️ CZYSZCZENIE:
Regularnie usuwaj stare pliki aby oszczędzić miejsce na dysku.
Aplikacja NIE usuwa plików automatycznie.

📊 FORMATY:
- Wyekstrahowane DMPy: format tekstowy (.txt)
- Recenzje: format tekstowy (.txt)
- Cache: format JSON (.json)
""", encoding='utf-8')

    print(f"{Colors.GREEN}✓ README.txt utworzone w input/ i output/{Colors.END}")
    return True

def create_documentation():
    """Tworzy główny plik instrukcji."""
    print_step("📚 Tworzenie dokumentacji użytkownika", Colors.BLUE)

    dist_path = Path('dist/DMP-ART')
    doc_path = dist_path / 'INSTRUKCJA.txt'

    doc_content = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║                DMP-ART - INSTRUKCJA OBSŁUGI                              ║
║                                                                           ║
║         Data Management Plan Assessment and Response Tool                 ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════
  🚀 SZYBKI START
═══════════════════════════════════════════════════════════════════════════

1. URUCHOMIENIE APLIKACJI
   → Kliknij dwukrotnie na plik: DMP-ART.exe
   → Poczekaj aż otworzy się okno przeglądarki (około 3 sekundy)
   → Aplikacja jest gotowa gdy zobaczysz stronę główną DMP-ART

2. PRZETWARZANIE PLIKU
   → Wrzuć pliki PDF/DOCX do folderu "input/"
   → W aplikacji kliknij "Wybierz plik" lub przeciągnij plik
   → Kliknij "Prześlij i przetwórz"
   → Poczekaj na ekstrakcję (10-60 sekund zależnie od rozmiaru)

3. RECENZJA
   → Aplikacja automatycznie podzieli DMP na 14 sekcji Science Europe
   → Użyj szybkich komentarzy z rozwijanej listy
   → Dodaj własne uwagi w polach tekstowych
   → Zapisz recenzję klikając "Zapisz feedback"

4. EKSPORT
   → Kliknij "Eksportuj feedback do pliku"
   → Plik zapisze się w folderze "output/reviews/"
   → Możesz otworzyć go w Notatniku lub Wordzie

═══════════════════════════════════════════════════════════════════════════
  📁 STRUKTURA FOLDERÓW
═══════════════════════════════════════════════════════════════════════════

DMP-ART/
│
├── DMP-ART.exe          ← GŁÓWNY PLIK - uruchamiaj ten plik
│
├── input/               ← Wrzuć tu pliki PDF/DOCX do recenzji
│   └── README.txt       ← Instrukcja dla folderu input
│
├── output/              ← Tutaj zapisują się wszystkie wyniki
│   ├── dmp/             ← Wyekstrahowane plany DMP
│   ├── reviews/         ← Twoje recenzje
│   └── cache/           ← Cache (można usuwać)
│
└── config/              ← Szablony komentarzy (edytowalne!)
    ├── quick_comments.json    ← Szybkie komentarze
    ├── newcomer.json          ← Kategoria: Dla początkujących
    ├── mising.json            ← Kategoria: Brakujące informacje
    └── ready.json             ← Kategoria: Gotowe komentarze

═══════════════════════════════════════════════════════════════════════════
  ⚙️ KONFIGURACJA
═══════════════════════════════════════════════════════════════════════════

EDYCJA SZABLONÓW KOMENTARZY:
1. Otwórz folder "config/"
2. Edytuj pliki JSON w Notatniku (lub edytorze JSON)
3. Zapisz zmiany
4. Uruchom ponownie DMP-ART.exe
5. Nowe komentarze pojawią się w aplikacji

PRZYKŁAD - dodanie nowego szybkiego komentarza (quick_comments.json):
[
  {
    "name": "Brak szczegółów",
    "text": "Proszę o podanie bardziej szczegółowych informacji..."
  }
]

═══════════════════════════════════════════════════════════════════════════
  🔧 ROZWIĄZYWANIE PROBLEMÓW
═══════════════════════════════════════════════════════════════════════════

❌ APLIKACJA NIE URUCHAMIA SIĘ
   → Sprawdź czy port 5000 jest wolny (zamknij inne aplikacje)
   → Uruchom ponownie DMP-ART.exe
   → Jeśli problem się powtarza, uruchom jako Administrator

❌ PRZEGLĄDARKA SIĘ NIE OTWIERA
   → Otwórz ręcznie: http://localhost:5000
   → Sprawdź czy aplikacja działa (powinno być okno konsoli)

❌ OCR NIE DZIAŁA (dla skanów PDF)
   → Ta wersja standalone NIE zawiera Tesseract OCR
   → Aby użyć OCR, zainstaluj Tesseract:
     https://github.com/UB-Mannheim/tesseract/wiki
   → Po instalacji uruchom ponownie aplikację

❌ BŁĄD "FILE TOO LARGE"
   → Maksymalny rozmiar pliku: 16 MB
   → Skompresuj PDF lub podziel dokument

❌ EKSTRAKCJA NIE DZIAŁA POPRAWNIE
   → Upewnij się że dokument zawiera sekcję "Data Management Plan"
   → Sprawdź czy format jest zgodny ze standardem NCN/OSF
   → Skontaktuj się z supportem (link poniżej)

═══════════════════════════════════════════════════════════════════════════
  ⚡ SKRÓTY KLAWISZOWE (w aplikacji webowej)
═══════════════════════════════════════════════════════════════════════════

Ctrl+S         - Zapisz feedback
Ctrl+E         - Eksportuj do pliku
Tab            - Przejdź do następnego pola
Shift+Tab      - Wróć do poprzedniego pola

═══════════════════════════════════════════════════════════════════════════
  📊 INFORMACJE TECHNICZNE
═══════════════════════════════════════════════════════════════════════════

Wersja:            0.8.1 Standalone
Backend:           Python + Flask
Frontend:          HTML5 + JavaScript (Vanilla)
OCR:               Tesseract (wymaga instalacji systemowej)
Obsługiwane OS:    Windows 10/11, Linux, macOS
Wymagania:         ~500 MB miejsca na dysku

═══════════════════════════════════════════════════════════════════════════
  📞 POMOC I KONTAKT
═══════════════════════════════════════════════════════════════════════════

📧 Zgłoś problem:  https://github.com/gammaro85/DMP-ART/issues
📚 Dokumentacja:   https://github.com/gammaro85/DMP-ART
💡 FAQ:            https://github.com/gammaro85/DMP-ART/wiki

═══════════════════════════════════════════════════════════════════════════
  ⚖️ LICENCJA
═══════════════════════════════════════════════════════════════════════════

DMP-ART jest oprogramowaniem open-source.
Copyright (c) 2024 gammaro85
Licencja: MIT

═══════════════════════════════════════════════════════════════════════════

                    Dziękujemy za używanie DMP-ART! 🎉

═══════════════════════════════════════════════════════════════════════════
"""

    doc_path.write_text(doc_content, encoding='utf-8')
    print(f"{Colors.GREEN}✓ INSTRUKCJA.txt utworzona{Colors.END}")

    return True

def create_zip_distribution():
    """Pakuje dystrybucję do ZIP."""
    print_step("📦 Pakowanie do archiwum ZIP", Colors.YELLOW)

    zip_name = 'DMP-ART-Standalone.zip'
    dist_folder = 'dist/DMP-ART'

    if os.path.exists(zip_name):
        os.remove(zip_name)
        print(f"▶ Usunięto stary {zip_name}")

    print(f"▶ Tworzenie {zip_name}...")

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, 'dist')
                zipf.write(file_path, arcname)
                # Wyświetl tylko kluczowe pliki (nie spam całej listy)
                if file.endswith(('.exe', '.txt', '.json')) or file == 'DMP-ART':
                    print(f"  + {arcname}")

    zip_size = os.path.getsize(zip_name) / (1024 * 1024)  # MB
    print(f"\n{Colors.GREEN}✓ Utworzono: {zip_name} ({zip_size:.1f} MB){Colors.END}")

    return True

def print_final_summary():
    """Wyświetla podsumowanie buildu."""
    print_step("✅ BUILD ZAKOŃCZONY SUKCESEM!", Colors.GREEN)

    print(f"{Colors.BOLD}📦 GOTOWE DO DYSTRYBUCJI:{Colors.END}")
    print(f"\n  1. Archiwum ZIP:    DMP-ART-Standalone.zip")
    print(f"  2. Folder:          dist/DMP-ART/")
    print(f"\n{Colors.BOLD}🚀 TESTOWANIE:{Colors.END}")
    print(f"  cd dist/DMP-ART")
    print(f"  ./DMP-ART.exe         (Windows)")
    print(f"  ./DMP-ART             (Linux/Mac)")
    print(f"\n{Colors.BOLD}📤 DYSTRYBUCJA:{Colors.END}")
    print(f"  - Wyślij użytkownikom: DMP-ART-Standalone.zip")
    print(f"  - Instrukcje są w środku: INSTRUKCJA.txt")
    print(f"\n{Colors.YELLOW}⚠️  UWAGA OCR:{Colors.END}")
    print(f"  Ta wersja standalone NIE zawiera Tesseract OCR.")
    print(f"  Użytkownicy będą musieli zainstalować Tesseract osobno")
    print(f"  jeśli chcą przetwarzać skany PDF.")
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}\n")

def main():
    """Główna funkcja buildu."""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}    DMP-ART STANDALONE BUILD SCRIPT    {Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

    steps = [
        ("Czyszczenie", clean_previous_builds),
        ("Build executable", build_executable),
        ("Struktura folderów", create_distribution_structure),
        ("Kopiowanie config", copy_config_files),
        ("README files", create_readme_files),
        ("Dokumentacja", create_documentation),
        ("Pakowanie ZIP", create_zip_distribution),
    ]

    for step_name, step_func in steps:
        if not step_func():
            print(f"\n{Colors.RED}{'='*60}{Colors.END}")
            print(f"{Colors.RED}{Colors.BOLD}❌ BUILD FAILED at: {step_name}{Colors.END}")
            print(f"{Colors.RED}{'='*60}{Colors.END}\n")
            sys.exit(1)

    print_final_summary()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Build cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}CRITICAL ERROR: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
