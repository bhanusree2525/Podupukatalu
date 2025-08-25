import os
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

_cached_client: Optional[Client] = None


def get_supabase_client() -> Client:
    global _cached_client
    if _cached_client is not None:
        return _cached_client
    load_dotenv(override=False)
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_ANON_KEY")
    _cached_client = create_client(url, key)
    return _cached_client
