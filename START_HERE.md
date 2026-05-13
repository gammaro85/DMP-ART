# DMP-ART - Quick Start Guide

## Pierwsze uruchomienie

### 1. Zainstaluj zależności
```powershell
# Utwórz środowisko wirtualne
python -m venv venv

# Aktywuj środowisko
.\venv\Scripts\Activate.ps1  # PowerShell
# LUB
venv\Scripts\activate.bat    # CMD

# Zainstaluj pakiety
pip install -r requirements.txt
```

### 2. (Opcjonalnie) Zainstaluj OCR
Jeśli chcesz przetwarzać zeskanowane PDF-y:
```powershell
# Pobierz i zainstaluj Tesseract OCR
# https://github.com/UB-Mannheim/tesseract/wiki
# Upewnij się, że instalujesz pakiety językowe: Polski (pol) i Angielski (eng)
```

## Codzienne użycie

### Tryb deweloperski (development)
**Kiedy używać:** Tworzenie zmian, testowanie, debugowanie

**PowerShell:**
```powershell
.\dev.ps1
```

**CMD:**
```cmd
dev.bat
```

**Ręcznie:**
```powershell
python app.py
```

🌐 Otwórz: http://localhost:5000

✨ **Korzyści:**
- Automatyczne przeładowanie przy zmianach w kodzie
- Szczegółowe komunikaty błędów
- Szybkie iteracje podczas rozwoju

---

### Tryb produkcyjny (production)
**Kiedy używać:** Udostępnianie innym, stabilne wdrożenie

**PowerShell:**
```powershell
.\prod.ps1
```

**PowerShell z opcjami:**
```powershell
.\prod.ps1 -Workers 8 -Port 8080 -Host "127.0.0.1"
```

**CMD:**
```cmd
prod.bat
```

🌐 Otwórz: http://localhost:5000

✨ **Korzyści:**
- Lepsza wydajność (wiele workerów)
- Bezpieczniejsze (brak debug mode)
- Stabilne dla wielu użytkowników

---

## Skróty klawiszowe w skryptach

### dev.ps1 / dev.bat
- Uruchamia Flask w trybie debug
- Auto-reload włączony
- Port 5000 (domyślny)

### prod.ps1 / prod.bat
- Uruchamia gunicorn z 4 workerami (domyślnie)
- Automatycznie instaluje gunicorn jeśli brakuje
- Generuje SECRET_KEY jeśli nie jest ustawiony

### prod.ps1 opcje:
```powershell
-Workers <liczba>   # Liczba procesów roboczych (domyślnie: 4)
-Port <port>        # Port serwera (domyślnie: 5000)
-Host <host>        # Host (domyślnie: 0.0.0.0 - dostęp z sieci)
```

**Przykłady:**
```powershell
# 8 workerów na porcie 8080
.\prod.ps1 -Workers 8 -Port 8080

# Tylko localhost (bez dostępu z sieci)
.\prod.ps1 -Host "127.0.0.1"
```

---

## Konfiguracja zaawansowana

### Zmienne środowiskowe (opcjonalne)

1. Skopiuj przykładowy plik:
```powershell
cp .env.example .env
```

2. Edytuj `.env` i ustaw wartości:
```
SECRET_KEY=twój-losowy-sekretny-klucz
GUNICORN_WORKERS=8
GUNICORN_PORT=5000
```

3. Załaduj przed uruchomieniem:
```powershell
# PowerShell
Get-Content .env | ForEach-Object {
    $name, $value = $_.split('=')
    Set-Content env:\$name $value
}

# Potem uruchom
python app.py  # lub gunicorn...
```

---

## Rozwiązywanie problemów

### "python: command not found"
- Sprawdź czy Python jest zainstalowany: `python --version`
- Dodaj Python do PATH (Windows)

### "gunicorn: command not found" (prod.ps1)
- Skrypt automatycznie zainstaluje gunicorn
- Lub ręcznie: `pip install gunicorn`

### "Tesseract not found" (OCR)
- Pobierz: https://github.com/UB-Mannheim/tesseract/wiki
- Dodaj do PATH: `C:\Program Files\Tesseract-OCR`

### Port 5000 zajęty
- Użyj innego portu: `.\prod.ps1 -Port 8080`
- Lub zabij proces: `Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process`

---

## Kolejne kroki

1. 📖 Przeczytaj [BUILD.md](BUILD.md) - szczegółowa dokumentacja wdrożenia
2. 🔧 Zobacz [CLAUDE.md](.claude/CLAUDE.md) - architektura i wzorce kodu
3. 📝 Sprawdź [HISTORY.md](HISTORY.md) - changelog i historia wersji

---

**Wsparcie:** W razie problemów zajrzyj do dokumentacji lub utwórz issue na GitHubie.
