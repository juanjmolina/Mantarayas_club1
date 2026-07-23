# Mantarayas — panel del club (Streamlit)

Misma estructura que ya usas y funciona en Streamlit Community Cloud: el panel completo (HTML/CSS/JS) vive embebido en `modules/html_content.py` y se renderiza como un **componente bidireccional real de Streamlit** — no como un simple `iframe` de solo lectura. Eso importa: los datos viajan por el mismo canal que usa cualquier control nativo de Streamlit, sin el límite de tamaño que tiene meter todo en la URL de la página (el mecanismo de la primera versión, que se quedaba corto con el volumen real de datos de un club).

## Cómo se guarda ahora

- Cada acción en el panel (crear un alumno, registrar un pago, marcar asistencia…) se guarda **al instante en tu navegador** — la ves reflejada de inmediato, como siempre.
- Unos segundos después (para no disparar un guardado por cada tecla que escribes), el panel **envía automáticamente** esos datos a la base de datos. No necesitas hacer nada.
- El botón **"Sincronizar ahora"** en la barra lateral sigue ahí por si quieres forzarlo de inmediato en vez de esperar los pocos segundos del guardado automático.
- Cuando abres el panel desde otro dispositivo, carga la última versión guardada en la base de datos.

## ⚠️ Una cosa que no pude verificar en mi entorno

No tengo forma de abrir un navegador real desde donde trabajo para probar visualmente el "apretón de manos" entre el panel y Streamlit (el protocolo que permite mandar datos sin pasar por la URL). Probé todo lo que se puede probar sin navegador — que el servidor arranca sin errores, que el componente se registra y sirve correctamente, que guardar y cargar de la base de datos funciona bien — pero **te pido que, apenas lo despliegues, hagas una prueba concreta**: haz un cambio en el panel (por ejemplo, agrega un alumno de prueba), espera unos segundos, y confirma que el texto bajo "Sincronizar ahora" cambie a "Sincronizado con la base de datos". Luego abre la app desde otro dispositivo o navegador y confirma que ese cambio ya aparece ahí. Si algo de eso no pasa, cuéntame exactamente qué viste y lo reviso.

## Uso local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Desplegar en Streamlit Community Cloud

1. Sube este repositorio a GitHub.
2. En [share.streamlit.io](https://share.streamlit.io), conecta tu repo y selecciona `app.py` como archivo principal.
3. (Opcional, recomendado para producción) En **Settings → Secrets** de tu app en Streamlit Cloud, agrega:
   ```toml
   DATABASE_URL = "postgresql://usuario:contraseña@host:5432/basededatos"
   ```
   Sin esto, usa SQLite (`db.sqlite3`), que en Streamlit Cloud **se borra cada vez que la app se reinicia o se redepliega** — bien para probar, no para datos que te importa conservar.

## ⚠️ Diferencias importantes frente a la versión con backend real (Flask)

- **Dos personas guardando cambios distintos casi al mismo tiempo:** el que guarda de último sobrescribe por completo lo que había guardado el primero (todo el club viaja como una sola foto conjunta, no por módulo). Con el guardado automático cada pocos segundos el riesgo es bajo, pero no es imposible.
- **El login no es seguro de verdad.** Seguimos con la pantalla de inicio de sesión y los roles (Super Admin, Profesor, etc.), pero es solo de interfaz — no hay servidor verificando contraseñas. Las contraseñas de ejemplo son las mismas de siempre (`admin` / `Mantarayas2026`, etc.) — cámbialas sabiendo que no ofrecen protección real.
- Si más adelante necesitas guardado por módulo (sin riesgo de sobrescritura) y seguridad real en el login, la versión con backend Flask (desplegable en Render o Azure) no tiene estas limitaciones — puedo dártela de nuevo cuando la quieras.

