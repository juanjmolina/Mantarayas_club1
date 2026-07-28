# Mantarayas — panel del club (Streamlit)

Misma estructura que ya usas y funciona en Streamlit Community Cloud: el panel completo (HTML/CSS/JS) vive embebido en `modules/html_content.py` y se renderiza como un **componente bidireccional real de Streamlit** — no como un simple `iframe` de solo lectura. Eso importa: los datos viajan por el mismo canal que usa cualquier control nativo de Streamlit, sin el límite de tamaño que tiene meter todo en la URL de la página (el mecanismo de la primera versión, que se quedaba corto con el volumen real de datos de un club).

## Cómo se guarda y se sincroniza ahora

- Cada acción en el panel (crear un alumno, registrar un pago, marcar asistencia…) se guarda **al instante en tu navegador** — la ves reflejada de inmediato, con confirmación visual en el propio botón.
- Unos segundos después, se envía automáticamente a la base de datos — no hace falta ningún clic aparte.
- El panel **pregunta cada 15 segundos** si hay algo nuevo guardado desde otro dispositivo, y si lo hay, lo trae solo — sin que nadie tenga que recargar la página. Así, un cambio hecho desde el celular aparece en el computador (y viceversa) en cuestión de segundos, no al instante-instante, pero sin intervención manual.
- El botón **"Sincronizar ahora"** sigue ahí por si quieres forzar el guardado de inmediato en vez de esperar.

## Base de datos

Esta app ya está pensada para usar una base de datos externa (Postgres) en vez del SQLite local — necesario porque Streamlit Cloud borra el SQLite local cada vez que la app se reinicia o se duerme por inactividad. Si conectaste Supabase (u otro Postgres) agregando `DATABASE_URL` en **Settings → Secrets** de tu app en Streamlit Cloud, ya estás usando esa base de datos real y persistente — perfecto, es justo lo que hace falta para que los datos sobrevivan reinicios y se vean iguales en todos los dispositivos.

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

