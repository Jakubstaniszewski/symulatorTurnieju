## Symulator turnieju piłkarskiego

Aplikacja desktopowa do zarządzania i symulowania turnieju piłkarskiego w stylu mistrzostw świata. Napisana w Pythonie z wykorzystaniem PyQt6.

---

### 🖥️ Funkcje

* ✅ Tworzenie własnych drużyn i przypisywanie im zawodników (max 16 drużyn, po 11 graczy).
* ✅ Możliwość wygenerowania losowego turnieju z polskimi nazwami drużyn i losowymi graczami.
* ✅ Statystyki zawodników (bramki, kartki, umiejętności).
* ✅ Symulacja meczów grupowych i fazy pucharowej (ćwierćfinały, półfinały, finał).
* ✅ Szczegółowy widok meczów, tabel grupowych i drabinki pucharowej.
* ✅ Debugging i eksport danych turnieju do pliku JSON.

---

### 🗂️ Struktura projektu

```
project/
│
├── main.py               # Główna aplikacja PyQt6
├── models.py             # Logika turnieju, drużyn, graczy i meczów
├── test_models.py        # Testy jednostkowe dla logiki
├── data.py               # Dane: imiona, nazwiska, drużyny
├── teams_snapshot_*.json # Eksportowane pliki z danymi turnieju

TournamentApp zawiera jedną instancję Tournament.
Tournament zawiera wiele (*) instancji Team oraz Match.
Team zawiera wiele (*) instancji Player.
Match jest powiązany z dwiema (2) instancjami Team.
TournamentApp dziedziczy po QMainWindow.
AddPlayerDialog dziedziczy po QDialog

```

---

### 🔧 Wymagania

* Python 3.9+
* PyQt6

#### Instalacja zależności:

```bash
pip install PyQt6
```

---

### ▶️ Uruchomienie aplikacji

```bash
python main.py
```

---

### 🧪 Testy jednostkowe

```bash
python test_models.py
```

---

### 📝 Eksport danych

Po rozpoczęciu turnieju lub wygenerowaniu losowego, automatycznie tworzony jest plik JSON:

* `teams_snapshot_round0.json` – przy ręcznym starcie
* `teams_snapshot_random.json` – przy losowym generowaniu

Plik zawiera:

* Statystyki drużyn
* Zawodników z ich umiejętnościami (`attack`, `defense`, `aggression`)
* Wyniki i statystyki turniejowe (gole, kartki)

---

### 🐞 Debugowanie

Wszystkie istotne akcje (dodanie drużyny, zawodnika, start turnieju, symulacja meczu) są logowane w konsoli jako `DEBUG` lub `INFO`:

Przykład:

```
[DEBUG] Dodano drużynę: Orły Warszawa
[DEBUG] Dodano zawodnika: Jan Kowalski do Orły Warszawa
[INFO] Turniej został rozpoczęty.
```
---

### 👨‍💻 Autor

Projekt stworzony w Pythonie przez:
- Jakub Staniszewski 096660
- Adam Szcześniak 096166

