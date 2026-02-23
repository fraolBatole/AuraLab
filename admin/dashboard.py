from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    from . import DEFAULT_DB_PATH
except ImportError:  # When run as a script (e.g., `streamlit run admin/dashboard.py`)
    DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "bot_database.db"


@st.cache_data(show_spinner=False)
def load_users(db_path: Path) -> pd.DataFrame:
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            """
            SELECT user_id, first_name, username, chat_id,
                   image_credits, video_credits,
                   current_plan, plan_expiry_date,
                   image_aspect_ratio, video_aspect_ratio,
                   created_at
            FROM users
            ORDER BY created_at DESC
            """,
            conn,
        )
    return df


def main() -> None:
    st.set_page_config(page_title="AuraLabs Admin", layout="wide")
    st.title("AuraLabs Admin Dashboard")

    db_path_str = st.sidebar.text_input("Database path", str(DEFAULT_DB_PATH))
    db_path = Path(db_path_str).expanduser().resolve()

    if not db_path.exists():
        st.error(f"Database not found at {db_path}")
        return

    users_df = load_users(db_path)
    total_users = len(users_df)
    total_image_credits = int(users_df["image_credits"].sum()) if total_users else 0
    total_video_credits = int(users_df["video_credits"].sum()) if total_users else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users", total_users)
    col2.metric("Image Credits", total_image_credits)
    col3.metric("Video Credits", total_video_credits)

    st.subheader("Users")
    st.dataframe(
        users_df,
        use_container_width=True,
    )

    st.markdown("---")
    st.subheader("Credit Management")

    with st.form("credit_form"):
        selected_ids = st.multiselect(
            "Select user IDs",
            options=users_df["user_id"].tolist(),
        )
        new_image = st.number_input("New image credits", value=10, min_value=0)
        new_video = st.number_input("New video credits", value=0, min_value=0)
        submitted = st.form_submit_button("Apply")

    if submitted:
        if not selected_ids:
            st.warning("Select at least one user")
        else:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE users SET image_credits=?, video_credits=? WHERE user_id IN ({','.join(['?']*len(selected_ids))})",
                    (new_image, new_video, *selected_ids),
                )
                conn.commit()
            load_users.clear()
            st.success(f"Updated {len(selected_ids)} user(s)")
            st.rerun()


if __name__ == "__main__":
    main()

