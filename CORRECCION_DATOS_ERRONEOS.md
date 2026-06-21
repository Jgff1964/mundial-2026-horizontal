# Corrección de datos erróneos

El problema no era el diseño ni Render. El parser anterior era demasiado permisivo:

- recorría todo el JSON/HTML de FIFA;
- aceptaba objetos internos que parecían partidos;
- convertía IDs enormes de FIFA en números de partido;
- terminaba armando un cuadro visualmente correcto con equipos mal ubicados.

Corrección aplicada:

- `fifa_client.py` ahora trabaja en modo estricto.
- Solo acepta partidos con número explícito entre 1 y 104.
- Ya no convierte IDs grandes en Match Number.
- Si FIFA no entrega una estructura limpia, la app muestra error en vez de inventar cruces.
- Se agregó `/api/debug` para revisar qué datos leyó.

Qué subir a GitHub:

- `fifa_client.py`
- `app.py`

Después:
Render → Manual Deploy → Deploy latest commit
