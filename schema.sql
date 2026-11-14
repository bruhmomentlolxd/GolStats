-- La API gratuita de football-data.org permite solo 10 consultas por minuto.
-- Por eso cada respuesta se guarda acá (caché): si pedimos lo mismo de nuevo y todavía es
-- "reciente", usamos lo guardado. Si la API falla o no hay internet, se muestra lo último guardado.

CREATE TABLE IF NOT EXISTS api_cache (
    cache_key  TEXT PRIMARY KEY,     -- ej: /competitions/PL/standings?
    payload    TEXT NOT NULL,        -- respuesta JSON de la API
    fetched_at REAL NOT NULL         -- momento de la descarga (segundos Unix)
);
