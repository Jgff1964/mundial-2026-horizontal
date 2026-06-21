# Mundial 2026 · Promiedos Horizontal

Versión corregida para celular horizontal con zoom.

## Fuente

- Usa Promiedos como fuente prioritaria para el cuadro.
- Si Promiedos todavía muestra semillas (`1A`, `2B`, `3A/B/C`), calcula el cuadro desde `zonas_validadas.json`.
- Si Promiedos ya muestra el cuadro armado con equipos reales, usa ese cuadro.

## Archivos a subir/reemplazar en GitHub

- `app.py`
- `promiedos_client.py`
- `bracket_logic.py`
- `renderer.py`
- `flags.py`
- `zonas_validadas.json`
- `requirements.txt`
- `Procfile`
- `render.yaml`

## Archivos viejos que se pueden borrar

- `fifa_client.py`
- `models.py`
- `aplicación.py`
- `modelos.py`
- `requisitos.txt`
- `LÉAME.md`

## Corrección visual aplicada

- Los rivales pendientes quedan en blanco.
- Se eliminan semillas y textos secundarios dentro de las cajas.
- Se eliminan prefijos de Promiedos como `AR`, `BR`, `DE`, etc.
- Se muestran banderas junto a la selección cuando el país está definido.


## FIX final banderas

Este fix limpia prefijos Promiedos y agrega banderas en tres capas: flags, renderer y bracket_logic.


## FIX BANDERAS REALES

El texto final ya no puede renderizar prefijos AR/BR/SA/AU/IR/CA/CO. El render usa display_country(), que devuelve bandera + país limpio.


## FIX actualización de posiciones

El botón ya no usa `zonas_validadas.json` como fuente fija. Intenta leer posiciones actuales desde Promiedos y, si no hay tablas suficientes en HTML, usa Cancha/La Nación como fallback.
