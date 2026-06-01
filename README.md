# SEEDiA Grant Intelligence System

System automatycznego monitorowania i scoringu grantów dla SEEDiA.

## Struktura projektu

```
seedia_grants/
├── .env                     # zmienne środowiskowe (nie commitować!)
├── .env.example             # szablon
├── requirements.txt         # Python dependencies
│
├── backend/
│   ├── config.py            # konfiguracja systemu
│   └── database.py          # Supabase client + operacje na bazie
│
├── ai/
│   └── extractor.py         # GPT-4o extraction + scoring + fiszki
│
├── crawlers/
│   ├── base_crawler.py      # klasa bazowa
│   ├── parp_crawler.py      # PARP nabory
│   ├── ncbr_crawler.py      # NCBR konkursy
│   ├── eit_crawler.py       # EIT Urban Mobility
│   ├── eu_portal_crawler.py # EU Funding & Tenders Portal (API)
│   ├── life_crawler.py      # LIFE / CINEA
│   └── interreg_crawler.py  # Interreg
│
├── scheduler/
│   ├── scanner.py           # główna logika daily scanu
│   ├── slack_alerts.py      # alerty Slack
│   └── cron_scheduler.py    # APScheduler (zastępuje Make.com)
│
├── migrations/
│   └── 001_initial_schema.sql  # schemat bazy (Supabase)
│
└── dashboard/               # React + Express dashboard
    ├── client/src/
    │   ├── pages/
    │   │   ├── GrantsPage.tsx       # lista grantów + filtry
    │   │   ├── GrantDetailPage.tsx  # szczegóły + fiszka + scoring
    │   │   └── StatsPage.tsx        # statystyki + KPI
    │   └── components/
    │       ├── Sidebar.tsx
    │       └── ScoreBadge.tsx
    └── server/
        ├── routes.ts          # API endpoints
        ├── storage.ts         # SQLite storage
        └── db.ts              # Drizzle ORM
```

## Uruchomienie

### 1. Backend Python (scanner + scheduler)

```bash
cd seedia_grants
pip install -r requirements.txt
cp .env.example .env  # uzupełnij Supabase URL + key

# Jednorazowy scan (test)
python scheduler/scanner.py

# Scheduler ciągły (codziennie 8:00 CEST, brief pon. 9:00 CEST)
python scheduler/cron_scheduler.py
```

### 2. Dashboard webowy

```bash
cd seedia_grants/dashboard
npm install
npm run dev        # http://localhost:5000
```

### 3. Migracja bazy Supabase

```sql
-- Wklej zawartość migrations/001_initial_schema.sql
-- w Supabase SQL Editor i uruchom
```

## Konfiguracja Supabase

1. Utwórz projekt na supabase.com
2. Przejdź do Settings → API
3. Skopiuj Project URL i service_role key
4. Wklej do .env:
   ```
   SUPABASE_URL=https://TWOJ_PROJEKT.supabase.co
   SUPABASE_SERVICE_KEY=eyJhbGci...
   ```

## Jak działa scoring 0–100

| Kryterium | Waga | Co mierzy |
|-----------|------|-----------|
| Dopasowanie produktowe | 25 | jCharge, solar shelter, e-paper, AI camera, incity.io |
| Dopasowanie tematyczne | 20 | smart city, mobility, renewable energy, AI |
| Kwalifikowalność SEEDiA | 15 | czy MŚP PL może aplikować |
| Potencjał finansowy | 15 | budżet, % dofinansowania |
| Bliskość komercjalizacji | 10 | czy prowadzi do sprzedaży/pilotażu |
| Trudność aplikacji | 10 | konsorcjum, papierologia |
| Deadline fit | 5 | czy realnie da się przygotować |

| Wynik | Rekomendacja |
|-------|-------------|
| 80–100 | **APPLY** — natychmiast do review |
| 65–79 | **STRONG WATCH** — sprawdzić ręcznie |
| 45–64 | **WATCH** — zostawić w radarze |
| <45 | **REJECT** — odrzucić |

## Alerty Slack

- **Score > 65** → natychmiastowy alert w kanale #grants
- **Deadline za 30/14/7/2 dni** → przypomnienia
- **Poniedziałek 9:00** → tygodniowy brief: Apply / Watch / Reject
