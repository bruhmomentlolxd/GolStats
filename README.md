# GolStats – App de fútbol con datos reales (football-data.org)

Python + Flask + SQLite + HTML/CSS/JS. Los datos vienen de la API gratuita de football-data.org.

## Instalación en Windows (forma sencilla)
1. Instalá Python 3.10 o superior desde https://www.python.org/downloads/windows/ y marca **"Add Python to PATH"** durante la instalación.
2. Extraé el ZIP completo.
3. Hacé doble clic en `INSTALAR_Y_ABRIR.bat`. La primera vez crea el entorno e instala las dependencias; necesita internet.
4. Si no existe `.env`, el archivo de inicio te permite pegar tu propia clave API. Para consultar partidos en vivo necesitas una clave de football-data.org: https://www.football-data.org/client/register
5. Se abrirá el navegador en **http://127.0.0.1:5000**. Dejá abierta la ventana negra mientras usás la app; para cerrarla, presioná Ctrl+C.

## Clave API (importante)
El archivo `.env` contiene tu clave privada y **nunca debe subirse a GitHub ni compartirse**. El repositorio incluye `.env.example` como plantilla sin secretos. Si ya tenías un `.env`, guardalo aparte antes de actualizar el proyecto.

## Qué hace
- `/` Partidos del día de las 12 competiciones del plan gratuito (flechas para cambiar de día, filtro "En vivo", se recarga solo cada 60 s si hay partidos en juego).
- `/competiciones/<CÓDIGO>` Tabla de posiciones, estadísticas personales (goles, asistencias, penales, promedio) y, al costado, los partidos por fecha con el botón "Partidos actuales".
- `/partido/<id>` Resumen (goles, tarjetas, cambios) y alineaciones con formación.

## Límites de la API gratuita
- 10 consultas por minuto → cada respuesta se guarda en SQLite (tabla `api_cache`) por unos minutos.
  Si la API falla o no hay internet, se muestran los últimos datos guardados.
- Algunos datos (alineaciones, eventos) pueden no estar disponibles según el plan o el partido; la app lo avisa.
- Para vaciar la caché: `flask --app app clear-cache`

## Estructura
- `app.py` crea la app · `config.py` configuración y lista de competiciones · `api.py` cliente de la API + caché
- `utils.py` horas (hora argentina), traducciones y conversión de datos · `routes.py` páginas
- `db.py` / `schema.sql` SQLite · `templates/` y `static/` interfaz
