# GolStats – App de fútbol (PC, celular y APK)

Python + Flask + SQLite. Datos de football-data.org (plan gratuito, 12 competiciones).

---------------------------------------------------------------------
## 💻 En la PC (Windows) – sin usar la consola

1. Instalá **Python 3.10+** desde https://www.python.org/downloads/ (marcá **"Add Python to PATH"**). Solo una vez.
2. Hacé **doble clic en `iniciar.bat`**.
   - La primera vez prepara todo solo (1–2 minutos, necesita internet).
   - Si no existe el archivo `.env`, te pide pegar tu API key de football-data.org.
   - Se abre GolStats en su propia ventana, como una app.
3. *(Opcional)* Doble clic en `crear_acceso_directo.bat` → aparece el icono **GolStats** en el Escritorio.
4. Para cerrar: cerrá la ventana negra.

**Ver la app en el celular por WiFi (sin publicarla):** usá `iniciar_para_celular.bat`.
Muestra una dirección tipo `http://192.168.x.x:5000`: abrila en el celular (misma red WiFi).
La primera vez Windows pregunta por el Firewall: elegí "Permitir acceso".

---------------------------------------------------------------------
## 📱 En el celular (app instalable) y APK

Un APK no puede "llevar" el servidor adentro: la app necesita estar publicada en internet.
Por eso son 3 pasos (todo gratis):

### Paso 1 – Subir el proyecto a GitHub
1. Creá una cuenta en https://github.com y un repositorio nuevo (ej. `golstats`).
2. Subí los archivos del proyecto (botón *Add file → Upload files*).
   **NO subas:** `.env` (tu API key), `venv/`, `instance/`.

### Paso 2 – Publicarlo en Render
1. Creá una cuenta en https://render.com (podés entrar con GitHub).
2. *New + → Blueprint* → elegí tu repositorio (usa el archivo `render.yaml`).
3. Cuando lo pida, en `FOOTBALL_API_KEY` pegá tu API key. Deploy.
4. Render te da una dirección tipo `https://golstats-xxxx.onrender.com`.

Notas del plan gratuito: si nadie la usa ~15 minutos se "duerme" y la primera carga tarda
~30–50 s. Los 10 pedidos por minuto de la API se comparten entre todos los visitantes
(por eso la app guarda los datos en una caché).

### Paso 3a – Instalarla como app (lo más simple)
Abrí tu dirección de Render en **Chrome del celular** → menú ⋮ → **"Instalar app"** (o
"Agregar a la pantalla principal"). Queda con su icono, abre a pantalla completa y funciona
como una app (Chrome crea un WebAPK real).

### Paso 3b – Obtener el archivo .APK
1. Entrá a https://www.pwabuilder.com y pegá tu dirección de Render → *Start*.
2. *Package for stores → Android* → completá las opciones (nombre: GolStats) → *Generate*.
3. Descargá el .zip: adentro está el `.apk`. **Guardá también el archivo de la clave** que incluye.
4. Pasalo al celular e instalalo (hay que permitir "instalar apps de orígenes desconocidos").
5. *(Opcional)* Para que la app no muestre la barra de direcciones: PWABuilder te da un archivo
   `assetlinks.json`. Copialo a la carpeta del proyecto (junto a `app.py`), subilo a GitHub y
   Render se actualiza solo. La app lo sirve en `/.well-known/assetlinks.json`.

(Los pasos exactos de PWABuilder pueden cambiar un poco con el tiempo.)

---------------------------------------------------------------------
## 🔐 Seguridad de la API key
- La key está solo en `.env` (PC) o en el panel de Render (online). El APK no la contiene.
- Como la compartiste en un chat, generá una nueva en football-data.org cuando termines y
  cambiala en `.env` / Render.

## Estructura
- `iniciar.bat`, `iniciar_para_celular.bat`, `crear_acceso_directo.bat` – instalación y arranque en Windows
- `run.py` – inicia el servidor y abre la ventana de la app
- `app.py` · `config.py` · `api.py` (cliente + caché SQLite) · `utils.py` · `routes.py` · `db.py` · `schema.sql`
- `templates/` · `static/` (CSS, JS, iconos, `manifest.webmanifest`, `sw.js` para la app instalable)
- `render.yaml` – configuración de publicación · `requirements.txt` – dependencias

## Para desarrolladores
- Modo desarrollo: `python app.py` → http://127.0.0.1:5000
- Vaciar caché de la API: `flask --app app clear-cache`
