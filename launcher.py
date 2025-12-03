#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DMP-ART Launcher - Standalone Executable Entry Point

Uruchamia Flask server i automatycznie otwiera przeglądarkę.
Obsługuje tryb bundled (PyInstaller) i tryb development.
"""

import sys
import os
import webbrowser
import time
from threading import Thread
import logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_bundled_environment():
    """
    Konfiguruje środowisko dla aplikacji zbundlowanej przez PyInstaller.
    Ustawia ścieżki do Tesseract OCR i innych zasobów.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_dir = sys._MEIPASS
        logger.info(f"Running in bundled mode. Base dir: {base_dir}")

        # Ścieżka do Tesseract (jeśli będzie zbundlowany)
        tesseract_path = os.path.join(base_dir, 'tesseract')
        if os.path.exists(tesseract_path):
            os.environ['TESSDATA_PREFIX'] = os.path.join(tesseract_path, 'tessdata')
            os.environ['PATH'] = tesseract_path + os.pathsep + os.environ.get('PATH', '')
            logger.info(f"Tesseract configured at: {tesseract_path}")
        else:
            logger.warning("Tesseract not found in bundle. OCR may not work for scanned PDFs.")

        return base_dir
    else:
        # Running in development mode
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Running in development mode. Base dir: {base_dir}")
        return base_dir

def setup_working_directories():
    """
    Tworzy strukturę folderów roboczych aplikacji.
    W trybie standalone używa folderów input/output obok .exe.
    """
    if getattr(sys, 'frozen', False):
        # W trybie bundled, foldery są obok .exe
        work_dir = os.path.dirname(sys.executable)
    else:
        # W trybie dev, używamy obecnego katalogu
        work_dir = os.path.dirname(os.path.abspath(__file__))

    # Zmiana katalogu roboczego
    os.chdir(work_dir)
    logger.info(f"Working directory: {work_dir}")

    # Tworzenie struktury folderów
    folders = [
        'input',
        'output',
        'output/dmp',
        'output/reviews',
        'output/cache',
        'config',
        'uploads',  # Tymczasowy folder dla uploadów
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        logger.debug(f"Ensured folder exists: {folder}")

    return work_dir

def open_browser_delayed(url='http://localhost:5000', delay=3):
    """
    Otwiera przeglądarkę po określonym opóźnieniu.

    Args:
        url: URL do otwarcia
        delay: Opóźnienie w sekundach
    """
    time.sleep(delay)
    logger.info(f"Opening browser: {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")
        print(f"\n⚠️  Nie udało się otworzyć przeglądarki automatycznie.")
        print(f"📱 Otwórz ręcznie: {url}")

def print_startup_banner(work_dir):
    """Wyświetla banner startowy z instrukcjami."""
    print("\n" + "="*60)
    print("  🚀 DMP-ART - Narzędzie do Recenzji Planów DMP")
    print("="*60)
    print(f"\n📂 Katalog roboczy: {work_dir}")
    print(f"📥 Pliki do przetworzenia: {os.path.join(work_dir, 'input')}")
    print(f"📤 Wyniki: {os.path.join(work_dir, 'output')}")
    print(f"\n🌐 Aplikacja uruchamia się na: http://localhost:5000")
    print(f"⏳ Przeglądarka otworzy się automatycznie za chwilę...")
    print(f"\n⚠️  ABY ZATRZYMAĆ APLIKACJĘ:")
    print(f"   - Zamknij to okno, LUB")
    print(f"   - Naciśnij Ctrl+C")
    print("="*60 + "\n")

def main():
    """Główna funkcja uruchamiająca aplikację."""
    try:
        # 1. Konfiguracja środowiska bundled
        base_dir = setup_bundled_environment()

        # 2. Tworzenie struktury folderów
        work_dir = setup_working_directories()

        # 3. Import aplikacji Flask (po konfiguracji środowiska!)
        logger.info("Importing Flask application...")
        from app import app

        # 4. Konfiguracja Flask dla trybu standalone
        app.config['UPLOAD_FOLDER'] = 'uploads'
        app.config['OUTPUT_FOLDER'] = 'output'
        app.config['CACHE_FOLDER'] = 'output/cache'
        app.config['DMP_FOLDER'] = 'output/dmp'
        app.config['REVIEWS_FOLDER'] = 'output/reviews'

        # 5. Wyświetlenie bannera
        print_startup_banner(work_dir)

        # 6. Uruchomienie przeglądarki w osobnym wątku
        browser_thread = Thread(
            target=open_browser_delayed,
            args=('http://localhost:5000', 3),
            daemon=True
        )
        browser_thread.start()

        # 7. Uruchomienie Flask servera
        logger.info("Starting Flask server...")
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False,  # Ważne dla bundled apps!
            threaded=True
        )

    except KeyboardInterrupt:
        print("\n\n👋 Zamykanie aplikacji...")
        logger.info("Application stopped by user (Ctrl+C)")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
        print(f"\n\n❌ BŁĄD KRYTYCZNY:")
        print(f"   {str(e)}")
        print(f"\n📧 Zgłoś problem na: https://github.com/gammaro85/DMP-ART/issues")
        input("\nNaciśnij Enter aby zamknąć...")
        sys.exit(1)

if __name__ == '__main__':
    main()
