# System Certyfikacji

System do wydawania i weryfikacji certyfikatów produktów z modułem śledzenia
łańcucha dostaw („od pola do stołu") opartym na własnym, prostym blockchainie.
Aplikacja webowa napisana w **Django 5.2**, z panelem administracyjnym (Jazzmin),
REST API (Django REST Framework) i publiczną weryfikacją certyfikatów przez kod QR.

> Projekt zaliczeniowy — grupa 3.

---

## Główne funkcje

- **Certyfikaty** — wystawianie przez jednostki certyfikujące, statusy
  (ważny / wygasły / unieważniony / oczekujący), generowanie kodu QR oraz
  szyfrowanego (Fernet) linku do publicznej weryfikacji, dołączanie pliku PDF.
- **Partie produktów** (`Product_batch`) — rejestracja partii powiązanych z
  certyfikatem, statusy obiegu (oczekujące / w obiegu / dostarczone / wycofane).
- **Łańcuch dostaw** — zdarzenia w łańcuchu (`Chain_event`) i podłańcuchy
  blockchain śledzące etapy: producent → przetwórca → dystrybutor → sklep,
  z danymi do wizualizacji na mapie (geokodowanie adresów przez Nominatim/OSM).
- **Blockchain** — własna implementacja (`SimpleBlockchain` + `SupplyChainSubchain`),
  hashowanie SHA-256, walidacja łańcucha, trwały zapis do plików JSON.
- **Weryfikacja konsumencka** — skan QR otwiera publiczną stronę certyfikatu,
  oceny/komentarze konsumentów oraz zgłaszanie oszustw (`Fraud_report`)
  z prostą ochroną antyspamową i captchą.
- **Konta** — firmy (`Company`) o różnych typach (producent, dystrybutor,
  magazyn, import, export) oraz jednostki certyfikujące (`Certifying_unit`),
  rejestracja jednostek na podstawie kodów (`RegistrationCode`).
- **Panel admina** — Jazzmin (motyw `darkly`).

---

## Stack technologiczny

| Obszar            | Technologia                                  |
|-------------------|----------------------------------------------|
| Backend           | Django 5.2, Django REST Framework            |
| Baza danych       | PostgreSQL (psycopg 3, połączenie przez SSL) |
| Panel admina      | django-jazzmin                               |
| Bezpieczeństwo    | cryptography (Fernet), django-simple-captcha, django-ratelimit |
| Pliki/obrazy      | Pillow, qrcode, pypdf, pydicom, opencv-contrib |
| Serwowanie statyków | WhiteNoise                                 |
| Produkcja         | gunicorn (deploy na Render)                  |

Wymagany **Python 3.12**.

---

## Struktura projektu

```
ProjektSystemCertyfikacji/            # katalog główny repo
├── manage.py
├── requirements.txt / Pipfile        # zależności
├── blockchain_data.json              # zapisany stan głównego blockchaina
├── subchains_data.json               # zapisane podłańcuchy (łańcuch dostaw)
│
├── main_app/                         # konfiguracja projektu Django
│   ├── settings.py                   # ustawienia (czyta zmienne z .env)
│   ├── urls.py                       # główny routing
│   └── wsgi.py / asgi.py
│
└── ProjektSystemCertyfikacji/        # główna aplikacja
    ├── models.py                     # modele domenowe
    ├── admin.py                      # konfiguracja panelu admina
    ├── serializers.py                # serializery DRF
    ├── signals.py / context_processors.py
    ├── all_views/                    # widoki (logowanie, certyfikaty, partie,
    │                                 #   zdarzenia, fraud, dashboardy, ...)
    ├── forms/                        # formularze Django
    ├── blockchain/                   # moduł blockchain (core, persistence,
    │                                 #   signals, middleware, urls, views)
    ├── utils/                        # geocoding, generator QR, czytnik PDF,
    │                                 #   szyfrowanie linku certyfikatu
    ├── management/commands/          # komendy zarządzające (m.in. statusy)
    ├── migrations/ · templates/ · static/
    └── media/                        # przesłane pliki (QR, PDF)
```

---

## Wymagania wstępne

- Python 3.12
- Dostęp do bazy PostgreSQL (projekt korzysta z hostowanej bazy Supabase/Render)

---

## Konfiguracja — zmienne środowiskowe

Ustawienia czytane są z pliku `.env` w katalogu głównym (przez `python-dotenv`).
Plik `.env` jest w `.gitignore` i **nie** powinien trafiać do repozytorium.

Utwórz `.env` z następującymi kluczami:

```dotenv
SECRET_KEY_ENV=<tajny klucz Django>
DEBUG_ENV=False                 # True/False
HOST_ENV=<host bazy PostgreSQL>
DATABASE_USER_ENV=<użytkownik bazy>
DATABASE_PASS_ENV=<hasło bazy>
FERNET_KEY_ENV=<klucz Fernet do szyfrowania linków certyfikatów>
```

Klucz Fernet możesz wygenerować tak:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Domyślna baza: `NAME=postgres`, `PORT=6543`, `sslmode=require`
(patrz `main_app/settings.py`).

---

## Instalacja i uruchomienie

```bash
# 1. Klon repozytorium
git clone <repo-url>
cd ProjektSystemCertyfikacji

# 2. Środowisko wirtualne
python -m venv .venv
.\.venv\Scripts\activate        # Windows (PowerShell)
# source .venv/bin/activate     # Linux / macOS

# 3. Zależności
pip install -r requirements.txt

# 4. Plik .env (patrz sekcja wyżej)

# 5. Migracje bazy
python manage.py migrate

# 6. Konto administratora
python manage.py createsuperuser

# 7. Pliki statyczne (do produkcji / WhiteNoise)
python manage.py collectstatic --noinput

# 8. Start serwera deweloperskiego
python manage.py runserver
```

Aplikacja: <http://127.0.0.1:8000/> · panel admina: <http://127.0.0.1:8000/admin/>

### Uruchomienie produkcyjne

```bash
gunicorn main_app.wsgi
```

---

## Komendy zarządzające

| Komenda                                         | Opis                                                  |
|-------------------------------------------------|-------------------------------------------------------|
| `python manage.py update_certificate_status`    | Oznacza jako `expired` certyfikaty po dacie `valid_to`. |

---

## Najważniejsze adresy (routing)

| Ścieżka                                   | Nazwa                     | Opis                                  |
|-------------------------------------------|---------------------------|---------------------------------------|
| `/`                                       | `home`                    | Strona główna                         |
| `/admin/`                                 | —                         | Panel administracyjny (Jazzmin)       |
| `/login/`, `/logout/`, `/register/`       | `login` / `logout` / `register` | Logowanie / rejestracja jednostki cert. |
| `/register_company/`                      | `register_company`        | Rejestracja firmy                     |
| `/certificate/<token>/`                   | `certificate_view`        | Publiczna weryfikacja certyfikatu (QR) |
| `/certificate/<token>/ratings/`           | `fetch_ratings`           | Oceny konsumenckie (JSON)             |
| `/certificate/<token>/pdf/`               | `certificate_pdf_download`| Pobranie PDF certyfikatu              |
| `/report_fraud/<token>/`                  | `report_fraud`            | Zgłoszenie oszustwa                   |
| `/certificates/...`                       | `add_cert`, `list_cert`, `cert_detail`, `edit_cert`, `delete_cert` | CRUD certyfikatów |
| `/product-batches/...`                    | `list/add/edit/delete/recall_product_batch` | Zarządzanie partiami |
| `/batches/<id>/events/...`                | `list_chain_events`, `add_chain_event` | Zdarzenia łańcucha dostaw |
| `/blockchain/`                            | —                         | Widoki/API blockchaina                |
| `/api/`                                   | —                         | REST API (DRF)                        |
| `/captcha/`                               | —                         | Endpointy captcha                     |

---

## Blockchain

Moduł `ProjektSystemCertyfikacji/blockchain/` zawiera autorską, uproszczoną
implementację blockchaina:

- **`SimpleBlockchain`** — główny łańcuch: rejestruje certyfikaty, partie i
  transfery; każdy blok jest hashowany SHA-256 i wiąże się z poprzednim.
- **`SupplyChainSubchain`** — osobny podłańcuch dla każdej partii produktu,
  rejestrujący etapy łańcucha dostaw (producent → przetwórca → dystrybutor →
  sklep) wraz z danymi do mapy.
- **Trwałość** — stan zapisywany jest automatycznie do `blockchain_data.json`
  i `subchains_data.json` (`blockchain/persistence.py`).
- **Integracja** — sygnały `post_save` (`blockchain/signals.py`) automatycznie
  dopisują nowe certyfikaty i partie do łańcucha.

Linki certyfikatów w kodach QR są szyfrowane kluczem **Fernet** i kodowane
URL-safe Base64 (`utils/redirect_certificate_url.py`).
