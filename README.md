# 🗄️ Szafki

System do zarządzania szafkami pracowniczymi. Stworzony z myślą o organizacjach z dużą ilością pracowników (700+), gdzie ręczne ogarnianie "kto ma którą szafkę" kończy się zazwyczaj chaosem i karteczkami przyklejanymi na szafki.

## Co to robi?

- **Ewidencja szafek** – miejsce, numer, zamek, płeć szatni, status
- **Przypisywanie pracowników** – kto, gdzie, od kiedy
- **Import pracowników** – z CSV, bo przepisywanie 700 osób ręcznie to zły pomysł
- **Historia zmian** – kto komu zabrał szafkę i dlaczego
- **Role użytkowników** – admin widzi wszystko, reszta tylko swój dział
- **Filtrowanie i wyszukiwanie** – bo weź z palca przeszukaj kilka tysięcy szafek i 700 pracowników

## Wymagania

- Python 3.10+
- PyQt6
- pandas (do obsługi CSV)
- argon2-cffi (hashowanie haseł, opcjonalnie – jest fallback na PBKDF2)

## Instalacja

```bash
# Klonowanie repo
git clone <https://github.com/N1hoo/Szafki>
cd Szafki

# Środowisko wirtualne (zalecane)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Zależności
pip install PyQt6 pandas argon2-cffi
```

## Uruchomienie

```bash
python main.py
```

Przy pierwszym uruchomieniu trzeba będzie się zalogować. Domyślne konto admina... cóż, sprawdź w kodzie albo stwórz przez skrypt. 😉

## Struktura projektu

```
├── main.py              # Punkt wejścia
├── database.py          # Obsługa bazy szafek (SQLite)
├── auth.py              # Użytkownicy i hasła
├── session.py           # Kto jest zalogowany
├── pracownicy.py        # Wczytywanie CSV z pracownikami
├── pracownicy.csv       # Dane pracowników
├── services/            # Logika biznesowa
├── ui/                  # Interfejs (PyQt6)
│   ├── dialogs/         # Okna dialogowe
│   ├── handlers/        # Obsługa zdarzeń
│   └── admin/           # Panele admina
└── ui_generated/        # Wygenerowane z Qt Designer
```

## Baza danych

Trzy bazy SQLite:
- `szafki.db` – szafki i przypisania
- `users.db` – użytkownicy systemu
- `history.db` - eventy

Jedna baza CSV:
- `pracownicy.csv` - automatyczny zrzut z systemu ERP

Tworzone automatycznie przy pierwszym uruchomieniu.

## Licencja

Projekt wewnętrzny. Rób z tym co chcesz, ale jak coś się zepsuje to nie moja wina.

---

*"Bo każda szafka zasługuje na swojego właściciela, a każdy pracownik na swoją szafkę."*
