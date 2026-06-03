from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

_client: Client = None

def get_db() -> Client:
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _client


def upsert_grant(grant_data: dict) -> dict:
    db = get_db()
    url = grant_data.get("url", "")
    # Check if grant already exists by URL
    if url:
        existing = db.table("grants").select("id").eq("url", url).execute()
        if existing.data:
            # Update existing
            grant_id = existing.data[0]["id"]
            update_data = {k: v for k, v in grant_data.items() if k != "id"}
            result = db.table("grants").update(update_data).eq("id", grant_id).execute()
            return result.data[0] if result.data else {"id": grant_id}
    # Insert new
    import uuid
    grant_data["id"] = str(uuid.uuid4())
    result = db.table("grants").insert(grant_data).execute()
    return result.data[0] if result.data else {}


def get_grants(filters: dict = None, limit: int = 100) -> list:
    db = get_db()
    query = db.table("grants").select("*").order("score_total", desc=True).limit(limit)
    if filters:
        for k, v in filters.items():
            query = query.eq(k, v)
    return query.execute().data


def get_grant_by_url(url: str) -> dict | None:
    db = get_db()
    result = db.table("grants").select("*").eq("url", url).execute()
    return result.data[0] if result.data else None


def get_sources(active_only: bool = True) -> list:
    db = get_db()
    query = db.table("sources").select("*").order("priority")
    if active_only:
        query = query.eq("active", True)
    return query.execute().data


def save_scan_log(log_data: dict):
    db = get_db()
    db.table("scan_logs").insert(log_data).execute()


def save_alert(alert_data: dict):
    db = get_db()
    db.table("alerts").insert(alert_data).execute()


def save_fiche(fiche_data: dict):
    db = get_db()
    grant_id = fiche_data.get("grant_id")
    if grant_id:
        existing = db.table("grant_fiches").select("id").eq("grant_id", grant_id).execute()
        if existing.data:
            db.table("grant_fiches").update(fiche_data).eq("grant_id", grant_id).execute()
            return
    db.table("grant_fiches").insert(fiche_data).execute()


def get_upcoming_deadlines(days: int = 30) -> list:
    db = get_db()
    from datetime import date, timedelta
    today = date.today().isoformat()
    future = (date.today() + timedelta(days=days)).isoformat()
    return (
        db.table("grants")
        .select("*")
        .gte("deadline", today)
        .lte("deadline", future)
        .in_("recommended_action", ["apply", "strong watch"])
        .order("deadline")
        .execute()
        .data
    )


def get_unalerted_high_score_grants() -> list:
    db = get_db()
    return (
        db.table("grants")
        .select("*")
        .gte("score_total", 65)
        .eq("alert_sent", False)
        .eq("ai_extracted", True)
        .execute()
        .data
    )


def mark_alert_sent(grant_id: str):
    db = get_db()
    db.table("grants").update({"alert_sent": True}).eq("id", grant_id).execute()
