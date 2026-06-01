"""
Uruchamia migrację bazy Supabase przez psycopg2 (direct Postgres connection).
Supabase udostępnia bezpośredni dostęp PostgreSQL na porcie 5432.

Użycie:
  export SUPABASE_URL=https://<ref>.supabase.co
  export SUPABASE_SERVICE_KEY=<twój_service_role_key>
  python3 migrations/run_migration.py
"""
import os
import sys

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

if not SUPABASE_URL or not SERVICE_KEY:
    print("ERROR: Ustaw zmienne środowiskowe SUPABASE_URL i SUPABASE_SERVICE_KEY")
    sys.exit(1)

PROJECT_REF = SUPABASE_URL.replace("https://", "").split(".")[0]

# Supabase direct Postgres connection string
DB_HOST = "aws-0-eu-central-1.pooler.supabase.com"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = f"postgres.{PROJECT_REF}"
DB_PASS = SERVICE_KEY

try:
    import psycopg2
except ImportError:
    print("Instaluję psycopg2...")
    os.system("pip install psycopg2-binary -q")
    import psycopg2

print(f"Łączę z bazą: {DB_HOST}:{DB_PORT}/{DB_NAME} jako {DB_USER}")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        connect_timeout=15,
        sslmode="require"
    )
    conn.autocommit = True
    cur = conn.cursor()

    sql_file = os.path.join(os.path.dirname(__file__), "001_initial_schema.sql")
    with open(sql_file, "r") as f:
        sql = f.read()

    print("Uruchamiam migrację...")
    cur.execute(sql)
    print("✓ Migracja zakończona sukcesem!")

    # Sprawdź tabele
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
    tables = cur.fetchall()
    print(f"Tabele w bazie: {[t[0] for t in tables]}")

    # Sprawdź źródła
    cur.execute("SELECT name FROM sources")
    sources = cur.fetchall()
    print(f"Źródła ({len(sources)}):")
    for s in sources:
        print(f"  - {s[0]}")

    cur.close()
    conn.close()

except Exception as e:
    print(f"✗ Błąd: {e}")
    sys.exit(1)
