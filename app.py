import os
from typing import Optional, Dict, Any, List
import streamlit as st
import pandas as pd
from supabase import Client
from supabase_client import get_supabase_client
from crud import insert_riddle, list_riddles, update_riddle, delete_riddle
from export_utils import export_to_csv_bytes, export_to_json_bytes

DIFFICULTIES = ["easy", "medium", "hard"]
CATEGORIES = ["traditional", "modern", "funny"]

st.set_page_config(page_title="Podupu Kathalu", page_icon="🧩", layout="wide")


def get_client() -> Client:
    return get_supabase_client()


def ensure_session_state():
    if "auth" not in st.session_state:
        st.session_state.auth = {"user": None}
    if "view" not in st.session_state:
        st.session_state.view = "Home"
    if "editing_id" not in st.session_state:
        st.session_state.editing_id = None


def sign_in(email: str, password: str) -> Optional[Dict[str, Any]]:
    client = get_client()
    try:
        res = client.auth.sign_in_with_password({"email": email, "password": password})
        return {"user": res.user, "session": res.session}
    except Exception as e:
        st.error(f"Login failed: {e}")
        return None


def sign_up(email: str, password: str) -> Optional[Dict[str, Any]]:
    client = get_client()
    try:
        res = client.auth.sign_up({"email": email, "password": password})
        st.success("Check your email to confirm the account.")
        return {"user": res.user, "session": res.session}
    except Exception as e:
        st.error(f"Sign up failed: {e}")
        return None


def sign_out():
    client = get_client()
    try:
        client.auth.sign_out()
        st.session_state.auth = {"user": None}
        st.success("Signed out.")
    except Exception as e:
        st.error(f"Sign out failed: {e}")


def sidebar():
    st.sidebar.title("🧩 Podupu Kathalu")
    st.sidebar.caption("Telugu riddles manager")

    # Auth controls (optional)
    with st.sidebar.expander("Authentication (optional)", expanded=False):
        if st.session_state.auth["user"]:
            st.success(f"Logged in as {st.session_state.auth['user'].email}")
            if st.button("Sign out"):
                sign_out()
        else:
            email = st.text_input("Email", key="auth_email")
            password = st.text_input("Password", type="password", key="auth_password")
            cols = st.columns(2)
            with cols[0]:
                if st.button("Sign in"):
                    res = sign_in(email, password)
                    if res and res["user"]:
                        st.session_state.auth = {"user": res["user"]}
                        st.rerun()
            with cols[1]:
                if st.button("Sign up"):
                    sign_up(email, password)

    view = st.sidebar.radio("Navigate", ["Home", "Add Riddle", "View Riddles"], index=["Home", "Add Riddle", "View Riddles"].index(st.session_state.view))
    st.session_state.view = view


def home_view():
    st.title("🧩 Podupu Kathalu")
    st.write("Welcome! Manage Telugu riddles: add, search, filter, edit, and export.")


def add_riddle_view():
    st.title("➕ Add Riddle")
    if not st.session_state.auth["user"]:
        st.info("Login to add riddles.")
        return
    with st.form("add_riddle_form", clear_on_submit=True):
        question = st.text_area("Question (Telugu)", height=120)
        answer = st.text_area("Answer (Telugu)", height=120)
        category = st.selectbox("Category", CATEGORIES)
        difficulty = st.selectbox("Difficulty", DIFFICULTIES)
        submitted = st.form_submit_button("Save")
        if submitted:
            if not question.strip() or not answer.strip():
                st.error("Question and Answer are required.")
            else:
                insert_riddle(None, question, answer, category, difficulty)
                st.success("Riddle saved!")


def editable_row(r: Dict[str, Any]):
    cols = st.columns([3, 3, 1.6, 1.6, 1.2])
    with cols[0]:
        q = st.text_area("Question", value=r["question"], key=f"q_{r['id']}", height=120)
    with cols[1]:
        a = st.text_area("Answer", value=r["answer"], key=f"a_{r['id']}", height=120)
    with cols[2]:
        c = st.selectbox("Category", options=CATEGORIES, index=CATEGORIES.index(r["category"]) if r["category"] in CATEGORIES else 0, key=f"c_{r['id']}")
    with cols[3]:
        d = st.selectbox("Difficulty", options=DIFFICULTIES, index=DIFFICULTIES.index(r["difficulty"]) if r["difficulty"] in DIFFICULTIES else 0, key=f"d_{r['id']}")
    with cols[4]:
        if st.button("Save", key=f"save_{r['id']}"):
            update_riddle(None, r["id"], {"question": q.strip(), "answer": a.strip(), "category": c, "difficulty": d})
            st.success("Updated.")
            st.session_state.editing_id = None
            st.rerun()
        if st.button("Cancel", key=f"cancel_{r['id']}"):
            st.session_state.editing_id = None
            st.rerun()


def view_riddles_view():
    st.title("📚 View Riddles")
    search = st.text_input("Search (Telugu/English)", "")
    c1, c2, c3, c4 = st.columns([1.2, 1.2, 1, 1])
    with c1:
        category = st.selectbox("Category", ["all"] + CATEGORIES)
    with c2:
        difficulty = st.selectbox("Difficulty", ["all"] + DIFFICULTIES)
    with c3:
        show_answers = st.checkbox("Show answers", value=False)
    with c4:
        load_limit = st.number_input("Limit", min_value=10, max_value=2000, value=500, step=10)

    rows = list_riddles(None, search, category if category != "all" else None, difficulty if difficulty != "all" else None, limit=int(load_limit))

    # Export
    exp_c1, exp_c2 = st.columns(2)
    with exp_c1:
        if st.download_button("Export CSV", data=export_to_csv_bytes(rows), file_name="podupu_kathalu.csv", mime="text/csv"):
            pass
    with exp_c2:
        if st.download_button("Export JSON", data=export_to_json_bytes(rows), file_name="podupu_kathalu.json", mime="application/json"):
            pass

    if not rows:
        st.info("No riddles found.")
        return

    # Table-like listing with edit/delete
    for r in rows:
        with st.expander(f"{r['question'][:80]}{'...' if len(r['question'])>80 else ''}  |  {r['category']} • {r['difficulty']}"):
            if st.session_state.editing_id == r["id"]:
                editable_row(r)
            else:
                st.write("Question:")
                st.write(r["question"])
                if show_answers:
                    st.write("Answer:")
                    st.write(r["answer"])
                colx1, colx2, colx3 = st.columns([1, 1, 4])
                with colx1:
                    if st.session_state.auth["user"] and st.button("Edit", key=f"edit_{r['id']}"):
                        st.session_state.editing_id = r["id"]
                        st.experimental_rerun()
                with colx2:
                    if st.session_state.auth["user"] and st.button("Delete", key=f"del_{r['id']}"):
                        delete_riddle(None, r["id"])
                        st.success("Deleted.")
                        st.experimental_rerun()
                with colx3:
                    st.caption(f"Category: {r['category']} | Difficulty: {r['difficulty']} | Created: {r['created_at']}")


def main():
    ensure_session_state()
    sidebar()
    if st.session_state.view == "Home":
        home_view()
    elif st.session_state.view == "Add Riddle":
        add_riddle_view()
    else:
        view_riddles_view()


if __name__ == "__main__":
    main()
