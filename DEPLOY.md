# SEEDiA Grant Scheduler — Deployment

## Wymagania
- Ubuntu/Debian z systemd
- Python 3.10+
- pip

---

## 1. Wgraj pliki na serwer

```bash
# Ze swojego komputera:
scp seedia_grants_system_v2.tar.gz user@TWOJ_SERWER:/opt/

# Na serwerze:
cd /opt
tar -xzf seedia_grants_system_v2.tar.gz
```

---

## 2. Zainstaluj zależności

```bash
cd /opt/seedia_grants
pip3 install -r requirements.txt
```

---

## 3. Utwórz plik .env

```bash
nano /opt/seedia_grants/.env
```

Wklej i uzupełnij swoimi kluczami:
```
GEMINI_API_KEY=<twój_klucz_gemini>
SUPABASE_URL=<twój_supabase_url>
SUPABASE_SERVICE_KEY=<twój_supabase_service_key>
SLACK_WEBHOOK=<twój_nowy_slack_webhook_url>
OPENAI_API_KEY=unused
```

> ⚠️ Nigdy nie wklejaj prawdziwych kluczy do plików wersjonowanych w Git.
> Klucze znajdziesz w: Supabase → Settings → API, Google AI Studio, Slack → api.slack.com/apps

Zabezpiecz plik:
```bash
chmod 600 /opt/seedia_grants/.env
```

---

## 4. Zainstaluj usługę systemd

```bash
# Ustaw swoją nazwę użytkownika w pliku service:
nano /opt/seedia_grants/seedia-scheduler.service
# Zmień: User=YOUR_LINUX_USER  →  np. User=ubuntu

# Skopiuj plik do systemd:
sudo cp /opt/seedia_grants/seedia-scheduler.service /etc/systemd/system/

# Przeładuj systemd i włącz usługę:
sudo systemctl daemon-reload
sudo systemctl enable seedia-scheduler
sudo systemctl start seedia-scheduler
```

---

## 5. Sprawdź status

```bash
# Status usługi:
sudo systemctl status seedia-scheduler

# Logi na żywo:
journalctl -u seedia-scheduler -f
```

Oczekiwany wynik po starcie:
```
[scheduler] SEEDiA Grant Scheduler starting...
[scheduler] Grant scan: Mon & Wed 07:00 UTC (09:00 CEST)
[scheduler] Weekly brief: Monday 07:30 UTC (09:30 CEST)
```

---

## 6. Ręczny scan (opcjonalnie)

Jeśli chcesz odpalić scan od ręki bez czekania na harmonogram:

```bash
cd /opt/seedia_grants
python3 run_scan.py
```

---

## Harmonogram

| Job | Dzień | Godzina CEST |
|-----|-------|--------------|
| Grant Scan | Poniedziałek + Środa | 09:00 |
| Weekly Brief (Slack) | Poniedziałek | 09:30 |

---

## Zatrzymanie / restart

```bash
sudo systemctl stop seedia-scheduler
sudo systemctl restart seedia-scheduler
```
