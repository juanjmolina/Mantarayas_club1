"""
app.py — Mantarayas · Panel del club
=====================================
Punto de entrada principal.

El HTML del panel está embebido en modules/html_content.py
100% Python — sin archivos .html externos en el repositorio.
GitHub detectará: Python 100%

Uso local:
    pip install -r requirements.txt
    streamlit run app.py

Producción (PostgreSQL):
    Agrega DATABASE_URL en variables de entorno o Streamlit Secrets.

## Cómo se guarda ahora (guardado automático)

A diferencia de la primera versión (que mandaba todos los datos metidos en
la URL de la página — funciona para datasets chicos, pero se rompe con el
tamaño real de datos de un club), esta versión usa el canal bidireccional
real de Streamlit: declara el panel como un "custom component" y los datos
viajan por la misma conexión que usa cualquier control nativo de
Streamlit, sin límite práctico de tamaño.

Cada cambio que haces en el panel se guarda al instante en tu navegador
(como siempre) y, unos segundos después (para no disparar un guardado por
cada tecla), se envía solo a la base de datos automáticamente. No hace
falta ningún clic — el botón "Sincronizar ahora" queda solo por si quieres
forzarlo de inmediato.
"""
import hashlib
import json
import os

import streamlit as st
import streamlit.components.v1 as components

from database.db import init_db, guardar_snapshot, cargar_snapshot, registrar_log
from modules.ui_helpers import pagina_config, ocultar_ui_streamlit
from modules.html_content import get_html

CLAVE = "mantarayas_v1"

# El componente de Streamlit necesita un archivo index.html real en disco
# (no puede servir un string en memoria). Lo escribimos a partir de
# modules/html_content.py — así el repositorio sigue sin tener ningún
# .html propio, pero Streamlit tiene qué servir.
COMPONENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".mantarayas_component")


@st.cache_resource(show_spinner=False)
def _preparar_componente():
    """
    Registra el componente UNA SOLA VEZ por proceso de servidor, no en
    cada re-ejecución del script. Streamlit vuelve a correr app.py de
    arriba a abajo después de cada guardado — si volviéramos a escribir
    el archivo y a llamar a declare_component() cada vez, corríamos el
    riesgo de que el panel se reinicie justo después de guardar (perdiendo
    el rastro de qué ya se sincronizó) en vez de simplemente recibir la
    confirmación. st.cache_resource asegura que esto pase una sola vez.
    """
    os.makedirs(COMPONENT_DIR, exist_ok=True)
    with open(os.path.join(COMPONENT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(get_html())
    return components.declare_component("mantarayas_panel", path=COMPONENT_DIR)


# ── 1. Configurar página (primera llamada a Streamlit) ────────
pagina_config()
ocultar_ui_streamlit()

# ── 2. Inicializar base de datos y preparar el componente (una sola vez) ──
init_db()
_mantarayas_component = _preparar_componente()

# ── 3. Cargar el snapshot más reciente de la base de datos ────
snapshot = cargar_snapshot(CLAVE)
datos_db = snapshot["datos"] if snapshot else {}
hash_db = snapshot["hash"] if snapshot else ""
ts_db = snapshot["actualizado_en"] if snapshot else ""

# ── 4. Renderizar el panel y escuchar lo que nos devuelva ──────
# Cuando el panel (JS) llama a guardarEnBD(), ese valor llega aquí como
# el valor de retorno del componente — sin pasar por la URL.
resultado = _mantarayas_component(
    datos_db=datos_db, hash_db=hash_db, ts_db=ts_db,
    key="mantarayas_panel", default=None,
)

# ── 5. Si llegó una foto nueva del panel, guardarla ─────────────
if resultado is not None:
    nuevo_hash = hashlib.md5(json.dumps(resultado, ensure_ascii=False).encode()).hexdigest()
    if st.session_state.get("_mantarayas_last_saved_hash") != nuevo_hash:
        ok = guardar_snapshot(CLAVE, resultado, "web")
        if ok:
            registrar_log("web", f"guardar:{CLAVE}")
        st.session_state["_mantarayas_last_saved_hash"] = nuevo_hash
        # Volver a correr el script para que el componente reciba, en su
        # próximo mensaje, la marca de tiempo y el hash YA actualizados
        # (si no, el panel confirmaría con datos de antes de guardar, o
        # ni siquiera confirmaría en el primer guardado de la app).
        st.rerun()
