def get_conn():
    """Retorna (conexión, motor). Motor: 'sqlite' | 'pg'."""
    if DATABASE_URL:
        try:
            import psycopg2

            print("DATABASE_URL:", DATABASE_URL)

            conn = psycopg2.connect(
                DATABASE_URL,
                connect_timeout=10
            )

            conn.autocommit = True
            return conn, "pg"

        except Exception as e:
            import streamlit as st
            st.error(f"ERROR POSTGRES: {repr(e)}")
            raise

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"
