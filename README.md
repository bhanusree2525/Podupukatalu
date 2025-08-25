# Podupu Kathalu (Streamlit + Supabase)

## Setup
1. Create a Supabase project and get `SUPABASE_URL` and `SUPABASE_ANON_KEY`.
2. In Supabase SQL editor, run the SQL from `sql/schema.sql`.
3. Copy `env.example` to `.env` and fill values.
4. Create a Python venv and install deps:
   - Windows PowerShell:
     - `python -m venv .venv`
     - `.venv\\Scripts\\Activate.ps1`
   - Install: `pip install -r requirements.txt`
5. Run: `streamlit run app.py`

## Auth (optional)
- Create users in Supabase Auth.
- Sign in from the sidebar. Only authenticated users can add/edit/delete; guests can view and export.

## Notes
- Search uses `ilike` on `question` and `answer`.
- Telugu matching may depend on DB collation; adjust as needed.
