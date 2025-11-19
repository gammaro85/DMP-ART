# DMP-ART - Przewodnik dla Data Stewardów

**Wersja:** 0.8.1
**Ostatnia aktualizacja:** 2025-11-18
**Dla kogo:** Data stewardzi i administratorzy danych oceniający DMP naukowców

---

## Spis treści

1. [Wprowadzenie](#wprowadzenie)
2. [Twój proces pracy](#twój-proces-pracy)
3. [Krok po kroku](#krok-po-kroku)
4. [Konfiguracja systemu](#konfiguracja-systemu)
5. [Najlepsze praktyki](#najlepsze-praktyki)
6. [Często zadawane pytania](#często-zadawane-pytania)

---

## Wprowadzenie

### Kim jesteś w tym systemie?

Jesteś **data stewardem** odpowiedzialnym za ocenę Planów Zarządzania Danymi (DMP) w wnioskach naukowców składanych do NCN przez system OSF.

### Co robi dla Ciebie DMP-ART?

DMP-ART to Twój asystent, który:

✅ **Automatycznie wyciąga** sekcję DMP z pełnego wniosku (PDF/DOCX)
✅ **Dzieli tekst** na 14 elementów zgodnie ze strukturą Science Europe
✅ **Proponuje gotowe komentarze** dla powtarzających się kwestii
✅ **Pozwala pisać unikalne** komentarze dla nietypowych przypadków
✅ **Kompiluje wszystko** w spójną recenzję dla naukowca
✅ **Zapisuje pliki** w uporządkowanej strukturze

### Twój typowy dzień

```
Poranek:
📥 Otrzymujesz 5 wniosków NCN do oceny (PDF)

Z DMP-ART (30 min/wniosek):
1. Wrzucasz PDF → system wyciąga DMP (5 sek)
2. Przeglądasz 14 sekcji → klikasz gotowe komentarze (20 min)
3. Dopisujesz 2-3 unikalne uwagi (5 min)
4. Kompilujesz recenzję → eksportujesz (5 min)
5. Gotowe! DMP w outputs/, recenzja w feedback/

Bez DMP-ART (2h/wniosek):
1. Szukasz DMP w 80-stronicowym PDF (15 min)
2. Kopiujesz ręcznie do Worda (20 min)
3. Piszesz każdy komentarz od zera (60 min)
4. Formatujesz dokument (15 min)
5. Gubisz pliki w folderach (10 min)
```

**Oszczędność czasu:** 75% (1.5h na wniosek!)

---

## Twój proces pracy

### Faza 1: Ekstrakcja DMP z wniosku

**Co się dzieje:**
```
Wniosek naukowca (PDF/DOCX 80 stron)
    ↓
DMP-ART automatycznie znajduje:
    - Start: "PLAN ZARZĄDZANIA DANYMI" lub "DATA MANAGEMENT PLAN"
    - Koniec: "OŚWIADCZENIA ADMINISTRACYJNE"
    ↓
Wyciągnięty DMP (2-5 stron)
    ↓
Zapisany w: outputs/DMP_Kowalski_J_OPUS_25_161125.docx
```

**Wsparcie dla:**
- ✅ Wnioski w języku polskim
- ✅ Wnioski w języku angielskim
- ✅ Wnioski mieszane (PL + EN)
- ✅ Skanowane PDF (z OCR)
- ✅ Niestandardowe formaty (fallback detection)

**Sukces:** 94.1% wniosków przetwarza bez problemu

### Faza 2: Podział na elementy struktury

**14 elementów DMP (Science Europe):**

```
1. Opis danych i pozyskiwanie
   1.1 Sposób pozyskiwania nowych danych
   1.2 Rodzaj, format i ilość danych

2. Dokumentacja i jakość
   2.1 Metadane i dokumenty towarzyszące
   2.2 Środki kontroli jakości

3. Przechowywanie i backup
   3.1 Przechowywanie podczas badań
   3.2 Bezpieczeństwo danych

4. Wymagania prawne
   4.1 Wymagania prawne i kodeksy postępowania
   4.2 Dane osobowe i wrażliwe

5. Udostępnianie i archiwizacja
   5.1 Sposób udostępniania
   5.2 Długoterminowe przechowywanie
   5.3 Ograniczenia dostępu
   5.4 Licencjonowanie danych

6. Odpowiedzialność i zasoby
   6.1 Osoby odpowiedzialne
   6.2 Środki finansowe
```

**Co widzisz:**
- Każdy element w osobnej karcie
- Wyekstrahowany tekst naukowca
- Pole na Twoje komentarze
- Gotowe sugestie komentarzy

### Faza 3: Recenzja każdego elementu

**Twoje narzędzia:**

#### A) Gotowe komentarze "jedno kliknięcie"

**Dla typowych przypadków:**

```
Przykład sekcji 1.1 - brak informacji:

[Kliknij] → Wstaw komentarz:
"❌ Brak opisu sposobu pozyskiwania danych.
Proszę uzupełnić informacje o:
- Metodę zbierania danych
- Narzędzia/urządzenia używane
- Częstotliwość zbierania danych"
```

**Kategorie gotowych komentarzy:**

🟢 **Ready to Use** - wszystko OK
- "✅ Sekcja kompletna i zgodna z wymaganiami"
- "✅ Opis szczegółowy i jasny"

🟡 **Newcomer Guidance** - dla początkujących
- "💡 Zalecam dodanie informacji o formacie plików"
- "💡 Warto wskazać konkretne repozytorium"

🔴 **Missing Info** - braki do uzupełnienia
- "❌ Brak opisu metadanych"
- "❌ Nie wskazano osoby odpowiedzialnej"

⚠️ **Concerns** - problemy do wyjaśnienia
- "⚠️ Planowany format zastrzeżony - rozważ otwarty"
- "⚠️ Czas przechowywania krótszy niż wymagane 10 lat"

#### B) Unikalne komentarze

**Dla nietypowych przypadków:**

```
Naukowiec pisze:
"Dane będą przechowywane na dysku Google Drive mojego
promotora, który po zakończeniu projektu je usunie."

Twój unikalny komentarz:
"⛔ KRYTYCZNE: Zaproponowane rozwiązanie nie spełnia wymagań NCN:
1. Google Drive nie jest certyfikowanym repozytorium
2. Brak gwarancji długoterminowego przechowywania
3. Usunięcie po projekcie narusza wymóg min. 10 lat

ROZWIĄZANIE:
Proszę wskazać certyfikowane repozytorium np.:
- MOST Wiedzy (repozytorium PG)
- Zenodo
- OpenAIRE"
```

#### C) Cytowanie fragmentów

**Gdy chcesz odnieść się do konkretnego zdania:**

```
1. Zaznacz fragment tekstu naukowca
2. Kliknij "Cytuj" (pojawia się przy zaznaczeniu)
3. Fragment wstawia się do komentarza:

❝ Dane będą przechowywane na dysku Google Drive ❞

⛔ To rozwiązanie nie spełnia wymagań...
```

### Faza 4: Kompilacja recenzji

**Co się dzieje:**

```
Kliknij "Skompiluj recenzję"
    ↓
System zbiera komentarze z 14 sekcji
    ↓
Generuje raport:

═══════════════════════════════════════
RECENZJA PLANU ZARZĄDZANIA DANYMI
═══════════════════════════════════════

Wniosek: OPUS-29
Naukowiec: dr Jan Kowalski
Data oceny: 2025-11-18

SEKCJA 1.1: Sposób pozyskiwania danych
❌ Brak opisu metodologii zbierania danych...

SEKCJA 1.2: Rodzaj i format danych
✅ Sekcja kompletna...

SEKCJA 2.1: Metadane
💡 Zalecam dodanie standardu metadanych...

[... wszystkie 14 sekcji ...]

═══════════════════════════════════════
PODSUMOWANIE
═══════════════════════════════════════
Elementy wymagające uzupełnienia: 3
Zalecenia: 5
Krytyczne uwagi: 1

Ocena ogólna: DO POPRAWY
```

### Faza 5: Eksport i organizacja plików

**Automatyczna organizacja:**

```
outputs/
├── DMP_Kowalski_J_OPUS_29_161125.docx    ← Wyekstrahowany DMP
└── cache_3f5b2c9d-8e1a-4b6c-9d2e.json    ← Cache z analizą

feedback/
└── feedback_Kowalski_J_OPUS_29_161125.txt ← Twoja recenzja

Powiązanie przez nazwę pliku:
DMP_Kowalski_J_OPUS_29_161125.docx
feedback_Kowalski_J_OPUS_29_161125.txt
         └─ Ta sama nazwa bazowa!
```

**Konwencja nazewnictwa:**

```
Format: {Type}_{Nazwisko}_{Imię}_{Konkurs}_{Edycja}_{DDMMYY}.{ext}

Przykłady:
DMP_Kowalski_J_OPUS_29_161125.docx
DMP_Nowak_A_PRELUDIUM_24_030625.docx
feedback_Kowalski_J_OPUS_29_161125.txt
feedback_Nowak_A_PRELUDIUM_24_030625.txt
```

**Korzyści:**
- ✅ Łatwe parowanie DMP ↔ recenzja
- ✅ Alfanumeryczne sortowanie
- ✅ Widoczne metadane w nazwie
- ✅ Brak konfliktów nazw

---

## Krok po kroku

### Krok 1: Wgraj wniosek

**Interfejs:**

```
┌─────────────────────────────────────────────┐
│  🌙 DMP-ART                    [Tryb ciemny] │
├─────────────────────────────────────────────┤
│                                              │
│   ┌─────────────────────────────────────┐  │
│   │  📄 Przeciągnij wniosek tutaj      │  │
│   │                                     │  │
│   │         lub                         │  │
│   │                                     │  │
│   │      [Wybierz plik]                │  │
│   └─────────────────────────────────────┘  │
│                                              │
│   Akceptowane: PDF, DOCX (max 16MB)         │
│   OCR: ✅ Automatyczne dla skanów           │
│                                              │
│           [Przetwórz wniosek]               │
└─────────────────────────────────────────────┘
```

**Akcje:**
1. Przeciągnij PDF/DOCX wniosku
2. Kliknij "Przetwórz wniosek"
3. Poczekaj 5-30 sekund

**Status processing:**
```
⏳ Analizuję dokument...
⏳ Wykrywam sekcję DMP...
⏳ Wydobywam zawartość...
⏳ Rozpoznaję strukturę...
✅ Gotowe!
```

### Krok 2: Przeglądaj wyekstrahowany DMP

**Interfejs główny:**

```
┌────────────────────────────────────────────────────────────────────┐
│  DMP-ART › Recenzja › DMP_Kowalski_J_OPUS_29_161125.docx           │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  SIDEBAR (fixed, prawa strona):                                    │
│  ┌─────────────────────────┐                                       │
│  │ 📍 NAWIGACJA            │  Główna zawartość:                    │
│  ├─────────────────────────┤                                       │
│  │ [1.1] [1.2]            │  ╔══════════════════════════════════╗ │
│  │ [2.1] [2.2]            │  ║ SEKCJA 1.1                       ║ │
│  │ [3.1] [3.2]            │  ║ Sposób pozyskiwania danych       ║ │
│  │ [4.1] [4.2]            │  ╠══════════════════════════════════╣ │
│  │ [5.1] [5.2] [5.3] [5.4]│  ║ 📄 TEKST NAUKOWCA:              ║ │
│  │ [6.1] [6.2]            │  ║                                  ║ │
│  ├─────────────────────────┤  ║ "Dane będą zbierane metodą..."  ║ │
│  │                         │  ║                                  ║ │
│  │ 💡 SZYBKIE KOMENTARZE   │  ║ [zaznacz tekst → Cytuj]         ║ │
│  ├─────────────────────────┤  ╠══════════════════════════════════╣ │
│  │ "✅ Kompletna sekcja"   │  ║ 📝 TWOJA RECENZJA:              ║ │
│  │ "💡 Dodaj standard..."  │  ║                                  ║ │
│  │ "❌ Brak opisu..."      │  ║ [pole tekstowe]                 ║ │
│  │                         │  ║                                  ║ │
│  │ [Więcej komentarzy...] │  ║ 250 znaków, 45 słów             ║ │
│  ├─────────────────────────┤  ╠══════════════════════════════════╣ │
│  │                         │  ║ 🏷️ KATEGORIE                   ║ │
│  │ 📂 KATEGORIE            │  ║ [Ready] [Newcomer] [Missing]    ║ │
│  ├─────────────────────────┤  ╚══════════════════════════════════╝ │
│  │ 🟢 Ready to Use         │                                       │
│  │ 🟡 Newcomer             │  [⬅️ Poprzednia]    [Następna ➡️]   │
│  │ 🔴 Missing Info         │                                       │
│  ├─────────────────────────┤                                       │
│  │ [Skompiluj recenzję]   │                                       │
│  └─────────────────────────┘                                       │
└────────────────────────────────────────────────────────────────────┘
```

**Kolorystyka (ciemny motyw):**

```css
Tło główne:        #1a1a1a (ciemny grafit)
Karty/Panele:      #2d2d2d (jaśniejszy grafit)
Tekst główny:      #ecf0f1 (jasny szary)
Akcent:            #3498db (niebieski)
Sukces:            #2ecc71 (zielony)
Uwaga:             #f39c12 (pomarańczowy)
Błąd:              #e74c3c (czerwony)
Sidebar:           #242424 (dark gray)
Hover:             #3a3a3a (lighter gray)
```

### Krok 3: Recenzuj sekcję po sekcji

**Workflow dla każdej sekcji:**

#### Scenariusz A: Sekcja OK

```
1. Czytasz tekst naukowca
2. Wszystko wygląda dobrze
3. Klikasz: "✅ Sekcja kompletna i zgodna z wymaganiami"
4. Komentarz wstawia się automatycznie
5. Klikasz "Następna ➡️"
```

#### Scenariusz B: Brakuje informacji

```
1. Czytasz tekst naukowca
2. Brakuje opisu formatu danych
3. Klikasz kategorię: [Missing Info]
4. Rozwijają się sugestie dla sekcji 1.2:
   - "❌ Brak opisu formatu danych"
   - "❌ Brak informacji o rozmiarze danych"
   - "❌ Nie wskazano typu danych"
5. Klikasz: "❌ Brak opisu formatu danych"
6. Komentarz wstawia się do pola recenzji
7. Opcjonalnie dopisujesz: "Proszę wskazać czy CSV, XML czy inny"
8. Klikasz "Następna ➡️"
```

#### Scenariusz C: Poważny problem

```
1. Czytasz: "Dane usunę po zakończeniu projektu"
2. To narusza wymagania NCN!
3. Piszesz unikalny komentarz:

   "⛔ KRYTYCZNE: Naruszenie wymagań NCN

   Zgodnie z wymogami NCN, dane muszą być
   przechowywane minimum 10 lat po zakończeniu
   projektu.

   WYMAGANE DZIAŁANIE:
   Proszę wskazać certyfikowane repozytorium
   i zobowiązać się do 10-letniego przechowywania."

4. Zaznaczasz problematyczny fragment
5. Klikasz "Cytuj"
6. Cytat dodaje się do komentarza
7. Klikasz "Następna ➡️"
```

### Krok 4: Skompiluj i wyeksportuj

**Kompilacja:**

```
1. Kliknij "Skompiluj recenzję" (sidebar, dół)
2. Pojawia się panel z podglądem:

   ┌──────────────────────────────────────┐
   │ RECENZJA - PODGLĄD                   │
   ├──────────────────────────────────────┤
   │                                      │
   │ [Pełna recenzja z wszystkich sekcji] │
   │                                      │
   ├──────────────────────────────────────┤
   │ [Skopiuj]  [Pobierz TXT]  [Zamknij] │
   └──────────────────────────────────────┘

3. Sprawdzasz recenzję
4. Klikasz "Pobierz TXT"
```

**Automatyczny zapis:**

```
System automatycznie zapisuje:

outputs/DMP_Kowalski_J_OPUS_29_161125.docx
  └─ Wyekstrahowany DMP

feedback/feedback_Kowalski_J_OPUS_29_161125.txt
  └─ Twoja recenzja

Oba pliki powiązane przez nazwę!
```

---

## Konfiguracja systemu

### 1. Struktura DMP - Definiowanie sekcji

**Gdzie:** Template Editor → zakładka "DMP Structure"

**Co możesz zmienić:**

```json
{
  "1. Data description and collection": [
    "How will new data be collected?",     ← Możesz edytować pytanie
    "What data (types, formats, volumes)?" ← Możesz dodać/usunąć
  ],
  "2. Documentation and data quality": [  ← Możesz zmienić tytuł sekcji
    "What metadata will be provided?",
    "How will data quality be ensured?"
  ]
}
```

**Przykład personalizacji:**

Chcesz dodać pytanie o zgodność z RODO w sekcji 4:

```
Przed:
"4. Legal requirements": [
  "What legal requirements apply?",
  "How will personal data be handled?"
]

Po edycji:
"4. Legal requirements": [
  "What legal requirements apply?",
  "How will personal data be handled?",
  "Is data processing compliant with GDPR?" ← NOWE!
]
```

**Efekt:** Nowe pytanie pojawi się jako sekcja 4.3 w interfejsie recenzji.

### 2. Szybkie komentarze - Twoja biblioteka

**Gdzie:** Template Editor → zakładka "Quick Comments"

**Interfejs:**

```
┌────────────────────────────────────────────┐
│ SZYBKIE KOMENTARZE                         │
├────────────────────────────────────────────┤
│                                            │
│ [➕ Dodaj nowy komentarz]                  │
│                                            │
│ ┌────────────────────────────────────────┐│
│ │ Nazwa: Kompletna sekcja                ││
│ │ Tekst: ✅ Sekcja kompletna...          ││
│ │              [Edytuj] [Usuń]           ││
│ └────────────────────────────────────────┘│
│                                            │
│ ┌────────────────────────────────────────┐│
│ │ Nazwa: Brak formatu danych             ││
│ │ Tekst: ❌ Proszę uzupełnić...          ││
│ │              [Edytuj] [Usuń]           ││
│ └────────────────────────────────────────┘│
│                                            │
│ [... więcej komentarzy ...]               │
│                                            │
│              [Zapisz zmiany]               │
└────────────────────────────────────────────┘
```

**Dodawanie komentarza:**

```
1. Kliknij [➕ Dodaj nowy komentarz]
2. Wypełnij:
   Nazwa: Brak repozutorium
   Tekst: ❌ Nie wskazano repozytorium długoterminowego.
          Proszę wybrać jedno z certyfikowanych:
          - MOST Wiedzy (repozytorium PG)
          - Zenodo
          - OpenAIRE

3. Kliknij [Zapisz]
```

**Efekt:** Komentarz pojawi się w sidebararze podczas recenzji.

### 3. Kategorie - Komentarze dla sekcji

**Gdzie:** Template Editor → zakładki kategorii

**Domyślne kategorie:**

🟢 **Ready to Use** - dla kompletnych sekcji
🟡 **Newcomer Guidance** - dla początkujących
🔴 **Missing Info** - dla braków

**Tworzenie własnej kategorii:**

```
1. Kliknij [➕ Nowa kategoria]
2. Nazwa: "Concerns - GDPR"
3. Kliknij [Utwórz]
4. Nowa zakładka pojawia się w Template Editor
5. Dodaj komentarze specyficzne dla GDPR:

   Sekcja 4.1:
   - "⚠️ Weryfikacja zgody na przetwarzanie danych"
   - "⚠️ Czy przewidziano anonimizację?"

   Sekcja 4.2:
   - "⚠️ Brak informacji o okresie przechowywania danych osobowych"
```

**Efekt:** Kategoria "Concerns - GDPR" pojawi się w sidebararze recenzji.

### 4. Kustomizacja dla pojedynczego elementu

**Przykład: Sekcja 1.2 (Format danych)**

**Chcesz mieć specjalne komentarze tylko dla 1.2:**

```
Template Editor → Kategoria "Missing Info"

Sekcja 1.1:
- "❌ Brak opisu metodologii"
- "❌ Brak informacji o narzędziach"

Sekcja 1.2: ← TUTAJ KUSTOMIZUJESZ
- "❌ Brak opisu formatu (CSV, JSON, XML?)"
- "❌ Brak informacji o rozmiarze danych"
- "❌ Brak informacji o strukturze plików"
- "💡 Zalecam otwarty format (nie Excel)"
```

**Podczas recenzji:**

```
Gdy jesteś w sekcji 1.2:
- Klikasz [Missing Info]
- Widzisz TYLKO komentarze dla 1.2
- Wybierasz odpowiedni
```

**Gdy jesteś w sekcji 1.1:**

```
- Klikasz [Missing Info]
- Widzisz TYLKO komentarze dla 1.1
- To są zupełnie inne komentarze!
```

---

## Najlepsze praktyki

### Organizacja pracy

**Strategia "Batch Processing":**

```
1. Rano: Wgraj wszystkie wnioski (10-20 szt.)
   → System przetwarza w tle
   → Kawa ☕

2. Przed południem: Recenzuj wnioski proste (5-6 szt.)
   → Głównie gotowe komentarze
   → 20-30 min/wniosek

3. Po południu: Recenzuj wnioski złożone (2-3 szt.)
   → Więcej unikalnych komentarzy
   → 40-50 min/wniosek

4. Koniec dnia: Kompilacja i eksport wszystkich recenzji
   → 5 min sumaryczny przegląd
```

### Używanie kategorii

**System 4 kategorii:**

🟢 **Ready to Use** → ~10% wniosków
- Kompletne DMP, brak uwag
- Szybkie "✅ OK"

🟡 **Newcomer Guidance** → ~40% wniosków
- Młodzi naukowcy, pierwsze wnioski
- Dużo "💡 Zalecam..."
- Ton pomocny, edukacyjny

🔴 **Missing Info** → ~40% wniosków
- Luki w opisie
- "❌ Proszę uzupełnić..."
- Konkretne brakujące elementy

⚠️ **Concerns** → ~10% wniosków
- Problemy wymagające wyjaśnienia
- "⚠️ Wymaga doprecyzowania..."
- Kwestie do przemyślenia

### Pisanie unikalnych komentarzy

**Wzór 3C:**

1. **Context** (Kontekst) - Co jest problemem?
2. **Consequence** (Konsekwencja) - Dlaczego to ważne?
3. **Correction** (Korekta) - Jak to naprawić?

**Przykład:**

```
BAD:
"Niewystarczający opis repozytorium."

GOOD:
"⚠️ KONTEKST:
Wskazano tylko 'repozytorium uniwersyteckie' bez szczegółów.

KONSEKWENCJA:
Nie można zweryfikować czy repozytorium spełnia wymogi:
- Długoterminowe przechowywanie (10 lat)
- Dostępność publiczna
- Przydzielanie DOI

KOREKTA:
Proszę wskazać konkretne repozytorium, np.:
- MOST Wiedzy (mostw danych.pg.edu.pl)
- Zenodo (zenodo.org)
I potwierdzić, że spełnia wymogi NCN."
```

### Cytowanie fragmentów

**Kiedy cytować:**

✅ **TAK:**
- Gdy fragment jest problematyczny
- Gdy naukowiec pisze coś niejasnego
- Gdy chcesz pokazać konkretny błąd

❌ **NIE:**
- Gdy cała sekcja jest zła (napisz ogólny komentarz)
- Gdy cytat jest bardzo długi (> 3 zdania)

**Dobre cytowanie:**

```
❝ Dane będą przechowywane na dysku zewnętrznym w biurze ❞

⛔ To rozwiązanie nie zapewnia:
- Backupu (co jeśli dysk ulegnie uszkodzeniu?)
- Długoterminowego dostępu (co po 10 latach?)
- Dostępności dla innych badaczy

Proszę wskazać certyfikowane repozytorium.
```

### Nazewnictwo plików

**Sprawdzaj metadane przed eksportem:**

```
System automatycznie wydobywa z wniosku:
- Nazwisko: Kowalski
- Imię: Jan
- Konkurs: OPUS
- Edycja: 29
- Data: 161125

Jeśli brakuje (plik: DMP_090424.docx):
- Zmień ręcznie przed eksportem
- Lub dodaj metadane w Template Editor
```

**Korzyść:**
Łatwe wyszukiwanie: `feedback_Kowalski_*`

---

## Często zadawane pytania

### Podstawy

**P: Ile czasu zajmuje przetworzenie wniosku?**

O:
- DOCX/PDF z tekstem: 5-10 sekund
- Skanowany PDF (OCR): 20-30 sekund
- 94.1% wniosków przetwarza się automatycznie

**P: Co jeśli DMP nie wyekstrahuje się poprawnie?**

O:
1. Sprawdź "Unconnected Text" (na dole strony recenzji)
2. Tekst może tam być - przekopiuj ręcznie
3. Jeśli brak - użyj "debug mode" i zgłoś problem

**P: Czy mogę pracować offline?**

O:
- Po wgraniu wniosku - TAK (dane w cache)
- Do wgrania nowego - potrzeba internetu
- Font Awesome (ikony) wymaga internetu

### Konfiguracja

**P: Jak zmienić język interfejsu?**

O: Obecnie tylko angielski interfejs, ale:
- Przetwarza polskie i angielskie DMP
- Możesz pisać komentarze po polsku
- Przyszła wersja: pełne tłumaczenie

**P: Czy mogę dodać więcej niż 14 sekcji?**

O: TAK!
1. Template Editor → DMP Structure
2. Dodaj nowe pytania do sekcji
3. System automatycznie numeruje (np. 1.3, 1.4)
4. Nowe sekcje pojawią się w recenzji

**P: Jak eksportować do DOCX zamiast TXT?**

O: Obecnie tylko TXT. Na liście TODO:
- Export do DOCX z formatowaniem
- Export do PDF
- Export do email template

### Workflow

**P: Czy mogę zapisać recenzję w trakcie?**

O: TAK!
- System auto-save'uje co 30 sekund
- Możesz zamknąć przeglądarkę i wrócić
- Cache jest ważny przez 24h

**P: Co jeśli omyłkowo usunę komentarz?**

O:
- Ctrl+Z działa w polu tekstowym
- Możesz kliknąć gotowy komentarz ponownie
- Nie ma auto-usuwania

**P: Jak masowo wyeksportować recenzje?**

O: Obecnie po kolei. TODO:
- Batch export wszystkich recenzji
- ZIP z DMP + recenzjami
- Excel summary sheet

### Problemy

**P: Sekcja jest pusta mimo że w DMP jest tekst**

O: Możliwe przyczyny:
1. Niestandardowe formatowanie → sprawdź "Unconnected Text"
2. Inny język niż PL/EN → zgłoś do rozszerzenia
3. Problem z wykrywaniem → użyj debug mode

**P: Gotowe komentarze się nie pokazują**

O:
1. Sprawdź czy wybrałeś kategorię ([Ready], [Missing], etc.)
2. Niektóre sekcje mogą nie mieć komentarzy w kategorii
3. Dodaj własne w Template Editor

**P: OCR nie działa na skanach**

O:
1. Sprawdź czy Tesseract zainstalowany: `tesseract --version`
2. Zainstaluj pakiety językowe: `tesseract-ocr-pol`
3. Zobacz INSTALLATION.md → sekcja OCR Setup

---

## Skróty klawiszowe

**Nawigacja:**
- `→` / `Tab` - Następna sekcja
- `←` / `Shift+Tab` - Poprzednia sekcja
- `Ctrl+K` - Skompiluj recenzję
- `Ctrl+S` - Zapisz progress (auto-save)

**Edycja:**
- `Ctrl+Z` - Cofnij w polu tekstowym
- `Ctrl+Y` - Ponów
- `Ctrl+A` - Zaznacz wszystko
- `Ctrl+C` - Kopiuj (działa na cytowanych fragmentach)

**Interfejs:**
- `Ctrl+D` - Przełącz dark/light mode
- `Esc` - Zamknij podgląd recenzji
- `F11` - Pełny ekran (lepszy focus)

---

## Twoja opinia

**DMP-ART jest dla Ciebie!**

Jeśli masz sugestie:
- Jakie kategorie komentarzy potrzebujesz?
- Jakiej funkcjonalności brakuje?
- Co można uprościć?

**Zgłoś:**
- GitHub Issues: https://github.com/gammaro85/DMP-ART/issues
- Email: [kontakt]
- Wewnętrzny system zgłoszeń

---

**Powodzenia w recenzjach! 🎯**

Oszczędzaj czas, podnoś jakość, pomagaj naukowcom.

---

**Wersja dokumentu:** 1.0
**Ostatnia aktualizacja:** 2025-11-18
**Autor:** DMP-ART Team
**Status:** Aktywny
