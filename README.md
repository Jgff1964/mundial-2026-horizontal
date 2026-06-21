# Mundial 2026 · Promiedos API Tablas

Versión que arma el cuadro usando las tablas de Promiedos.

## Fuente principal

La app usa el endpoint de Promiedos:

```txt
https://api.promiedos.com.ar/league/tables_and_fixtures/fjda
```

Ese endpoint fue identificado por el patrón público usado para otras ligas de Promiedos:
`https://api.promiedos.com.ar/league/tables_and_fixtures/{id}`.

## Qué hace

- Lee las tablas del Mundial desde Promiedos API.
- Ordena los grupos A-L según la tabla que devuelve Promiedos.
- Resuelve 1A, 2A, 1B, 2B, etc.
- Lee el cuadro de Promiedos desde la página visible como respaldo/superposición.
- Si Promiedos ya reemplazó semillas por países reales, usa esos países.
- Muestra bandera + país limpio.
- No muestra abreviaturas AR, BR, SA, etc.
- Si las tablas no se leen, muestra error; no inventa posiciones viejas.

## Archivos que deben quedar en GitHub

- `app.py`
- `bracket_logic.py`
- `flags.py`
- `promiedos_client.py`
- `renderer.py`
- `zonas_validadas.json`
- `requirements.txt`
- `Procfile`
- `render.yaml`
- `README.md`

## Archivos viejos que conviene borrar

- `fifa_client.py`
- `models.py`
- `standings_client.py`
- `aplicación.py`
- `modelos.py`
- `requisitos.txt`
- `LÉAME.md`
- cualquier `CORRECCION_*.md`

## Debug

Luego de publicar:

```txt
/api/debug
```

muestra:

- `api_url`
- `last_update`
- `last_error`
- `zones_source`
- `zones`
- `api_summary`
