"""
database/db.py
==============
Acceso a datos. SQLite por defecto, PostgreSQL en producción.
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime
from typing import Optional

DATABASE_URL = os.environ.get("DATABASE_URL", "")
DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "db.sqlite3"
)


def get_conn():
    """
    Retorna (conexion, motor)
    motor = sqlite | pg
    """

    if DATABASE_URL:
        try:
            import psycopg2

            url = DATABASE_URL.replace(
                "postgres://",
                "postgresql://",
                1
            )

            conn = psycopg2.connect(
                url,
                sslmode="require",
                connect_timeout=10,
            )

            conn.autocommit = True

            return conn, "pg"

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            raise RuntimeError(f"Error conectando PostgreSQL: {e}")

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    return conn, "sqlite"


def ph(engine: str):
    return "%s" if engine == "pg" else "?"


def init_db():

    conn, engine = get_conn()
    cur = conn.cursor()

    if engine == "sqlite":

        cur.executescript("""
            CREATE TABLE IF NOT EXISTS snapshots(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clave TEXT UNIQUE,
                datos TEXT,
                hash_datos TEXT,
                creado_en TEXT,
                actualizado_en TEXT
            );

            CREATE TABLE IF NOT EXISTS sync_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT,
                accion TEXT,
                creado_en TEXT
            );
        """)

        conn.commit()

    else:

        cur.execute("""
        CREATE TABLE IF NOT EXISTS snapshots(
            id SERIAL PRIMARY KEY,
            clave TEXT UNIQUE,
            datos JSONB,
            hash_datos TEXT,
            creado_en TIMESTAMPTZ DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ DEFAULT NOW()
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS sync_log(
            id SERIAL PRIMARY KEY,
            usuario TEXT,
            accion TEXT,
            creado_en TIMESTAMPTZ DEFAULT NOW()
        )
        """)

    conn.close()


def guardar_snapshot(clave, datos, usuario="web"):

    conn, engine = get_conn()

    cur = conn.cursor()

    js = json.dumps(datos, ensure_ascii=False)

    h = hashlib.md5(js.encode()).hexdigest()

    if engine == "sqlite":

        cur.execute("""
        INSERT INTO snapshots
        (clave,datos,hash_datos,creado_en,actualizado_en)

        VALUES(?,?,?,?,?)

        ON CONFLICT(clave)

        DO UPDATE SET

        datos=excluded.datos,

        hash_datos=excluded.hash_datos,

        actualizado_en=excluded.actualizado_en

        """,(clave,js,h,datetime.utcnow().isoformat(),datetime.utcnow().isoformat()))

        conn.commit()

    else:

        cur.execute("""
        INSERT INTO snapshots
        (clave,datos,hash_datos,actualizado_en)

        VALUES(%s,%s::jsonb,%s,NOW())

        ON CONFLICT(clave)

        DO UPDATE SET

        datos=EXCLUDED.datos,

        hash_datos=EXCLUDED.hash_datos,

        actualizado_en=NOW()
        """,(clave,js,h))

        cur.execute("""
        INSERT INTO sync_log(usuario,accion)

        VALUES(%s,%s)
        """,(usuario,f"guardar:{clave}"))
    
    conn.commit()
    conn.close()

    return True


def cargar_snapshot(clave)->Optional[dict]:

    conn, engine = get_conn()

    cur = conn.cursor()

    cur.execute(
        f"SELECT datos,hash_datos,actualizado_en FROM snapshots WHERE clave={ph(engine)}",
        (clave,)
    )

    row = cur.fetchone()

    conn.close()

    if not row:

        return None

    if engine=="pg":

        datos=row[0]

        return{
            "datos":datos,
            "hash":row[1],
            "actualizado_en":str(row[2])
        }

    datos=json.loads(row["datos"])

    return{

        "datos":datos,

        "hash":row["hash_datos"],

        "actualizado_en":row["actualizado_en"]

    }


def registrar_log(usuario,accion):

    conn,engine=get_conn()

    cur=conn.cursor()

    cur.execute(

        f"INSERT INTO sync_log(usuario,accion) VALUES({ph(engine)},{ph(engine)})",

        (usuario,accion)

    )

    if engine=="sqlite":

        conn.commit()

    conn.close()
