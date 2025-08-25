from typing import Any, Dict, List, Optional
from supabase import Client
from supabase_client import get_supabase_client

TABLE_NAME = "podupu_kathalu"


def insert_riddle(client: Optional[Client], question: str, answer: str, category: str, difficulty: str) -> Dict[str, Any]:
    sb = client or get_supabase_client()
    payload = {"question": question.strip(), "answer": answer.strip(), "category": category.strip(), "difficulty": difficulty.strip()}
    res = sb.table(TABLE_NAME).insert(payload).execute()
    return {"data": res.data, "count": res.count}


def list_riddles(client: Optional[Client], search_query: Optional[str] = None, category: Optional[str] = None, difficulty: Optional[str] = None, limit: int = 500) -> List[Dict[str, Any]]:
    sb = client or get_supabase_client()
    q = sb.table(TABLE_NAME).select("*").order("created_at", desc=True)
    if search_query:
        pattern = f"%{search_query}%"
        q = q.or_(f"question.ilike.{pattern},answer.ilike.{pattern}")
    if category:
        q = q.eq("category", category)
    if difficulty:
        q = q.eq("difficulty", difficulty)
    if limit:
        q = q.limit(limit)
    res = q.execute()
    return res.data or []


def update_riddle(client: Optional[Client], riddle_id: str, values: Dict[str, Any]) -> Dict[str, Any]:
    sb = client or get_supabase_client()
    res = sb.table(TABLE_NAME).update(values).eq("id", riddle_id).execute()
    return {"data": res.data, "count": res.count}


def delete_riddle(client: Optional[Client], riddle_id: str) -> int:
    sb = client or get_supabase_client()
    res = sb.table(TABLE_NAME).delete().eq("id", riddle_id).execute()
    return res.count or 0
