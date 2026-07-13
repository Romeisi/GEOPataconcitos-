# Guía de Presentación — GEOPataconcitos
### Sustentación en vivo · Proyecto Semestral Tópicos II (25% de la nota)

**Formato:** 8 min de demo técnica + 2 min de preguntas · Exponen las dos · Compartir pantalla · PPT opcional.
**Equipo:** Romeisi Paniagua y Paula Ramos.

> La evaluación es **práctica y en vivo**: no se trata de leer diapositivas, sino de
> demostrar que el ecosistema funciona de verdad. Mostrar cosas corriendo vale más que explicarlas.

---

## 0. Preparación (30 min antes — checklist)

**Reinicio limpio de la infraestructura (opcional, para arrancar sin basura previa):**
```bash
docker compose down -v          # apaga y borra la base de datos
docker compose up -d --build    # vuelve a levantar todo
docker compose exec api python -m pipeline.run_pipeline   # recarga los 261 puntos
```

Antes de exponer, deja TODO abierto y funcionando para no perder tiempo en vivo:

- [ ] `docker compose ps` muestra 4 contenedores en estado *Up* (db, mage, api, dashboard).
- [ ] Pipeline ya ejecutado una vez (los 261 puntos cargados en la BD).
- [ ] Pestañas del navegador abiertas y listas, en este orden:
  1. Trello (tablero del proyecto)
  2. `docs/arquitectura.drawio` abierto en https://app.diagrams.net
  3. Terminal con `docker compose ps` a la vista
  4. Mage AI → http://localhost:6789 (ya con sesión iniciada)
  5. API Swagger → http://localhost:8000/docs
  6. Dashboard → http://localhost:8501
- [ ] Ten a mano coordenadas de un patacón de prueba para el registro en vivo (ej. lat `9.0550`, lon `-79.4850`).
- [ ] Ensaya la demo completa **cronometrada al menos una vez**.

> **Login de Mage:** si pide usuario, entra con `admin@admin.com` / `admin`.

---

## Guion minuto a minuto

### 1 · Introducción + Trello — (0:00–1:00) 

**Hacer:** Compartir pantalla en Trello.

**Decir:**
> "Buenas. Somos Romeisi y Paula. Nuestro proyecto es **GEOPataconcitos**, un flujo de datos
> end-to-end para inventariar y monitorear los vertederos informales de basura de San Miguelito.
> Este es nuestro tablero ágil en Trello: dividimos el trabajo en las tres etapas —diseño, pipeline
> y capa de consumo—. Romeisi hizo [X] y Paula [Y]; aquí se ve el progreso de cada tarjeta."

Señala rápido: tareas hechas, asignación equitativa. **Máx 1 min.**

---

### 2 · Arquitectura — (1:00–2:30) 

**Hacer:** Cambiar al diagrama `arquitectura.drawio`.

**Decir** (traza el recorrido del dato con el cursor):
> "Todo vive dentro de **Docker**. La **fuente** es un GeoJSON con 261 focos levantados en campo.
> Un **script de Python (Extract & Load)**, orquestado por **Mage AI**, lee esa fuente y guarda los
> datos crudos en **PostgreSQL con PostGIS**. Luego **GeoPandas** limpia y convierte cada punto en
> una geometría POINT WGS84, y lo carga en la tabla final. Sobre esa base, **FastAPI** expone los
> datos como API REST, y **Streamlit** los consume y los pinta en un mapa interactivo. La fuente se
> mantiene viva porque los usuarios registran nuevos focos desde el dashboard."

---

### 3 · Ecosistema Docker — (2:30–3:15) 

**Hacer:** En la terminal, ejecutar en vivo:
```bash
docker compose ps
```

**Decir:**
> "Toda la infraestructura corre aislada y es reproducible. Con `docker compose up` se levantan cuatro
> contenedores: **PostgreSQL/PostGIS**, **Mage AI**, la **API FastAPI** y el **dashboard Streamlit**.
> Aquí están los cuatro en estado *Up*. Cualquiera puede clonar el repo y reproducir este entorno idéntico."

---

# ⭐ PUNTO 4 · Orquestación e Ingesta (Mage AI + GeoPandas) — (3:15–5:30) · **Paula**

> Este es el corazón técnico. Tómate tu tiempo aquí. La idea es que **entiendas de verdad** lo que
> muestras, para que suene natural y respondas preguntas sin trabarte.

### 4.0 · Conceptos que debes dominar antes (léelos hasta entenderlos)

**¿Qué es un "pipeline de datos"?**
Es una **línea de producción para datos**: igual que en una fábrica la materia prima pasa por
estaciones hasta salir un producto terminado, aquí los datos crudos pasan por pasos hasta quedar
limpios y guardados listos para usarse. Nuestro pipeline se llama `ingesta_vertederos`.

**¿Qué es "ETL / Extract–Transform–Load"?**
Son las tres estaciones clásicas de ese proceso:
- **Extract (Extraer):** traer los datos desde la fuente (nuestro GeoJSON de 261 focos).
- **Transform (Transformar):** limpiarlos y darles forma (quitar errores, convertir coordenadas en geometrías).
- **Load (Cargar):** guardarlos en la base de datos final (PostgreSQL/PostGIS).

**¿Qué es un "orquestador" y qué es Mage AI?**
Un orquestador es el **director de orquesta** del pipeline: decide **en qué orden** se ejecutan los
pasos, los **conecta** entre sí, los **programa** para que corran solos (ej. cada 12 horas) y avisa
si algo falla. **Mage AI** es la herramienta que usamos para eso; nos da una interfaz visual para ver
y correr el pipeline sin ejecutar comandos a mano.

**¿Qué es un "DAG"?**
Es el **mapa de los pasos y sus flechas**: significa "grafo dirigido acíclico". En cristiano: una
cadena de bloques donde cada uno alimenta al siguiente, siempre hacia adelante, sin volver atrás.
Nuestro DAG es: **Extraer → Transformar → Cargar**.

**¿Qué es GeoPandas y por qué lo usamos?**
Pandas es la librería estrella de Python para manejar tablas de datos. **GeoPandas** es Pandas
"con superpoderes geográficos": entiende **coordenadas y geometrías** (puntos, líneas, polígonos).
Nosotras la usamos para convertir cada par de números (longitud, latitud) en un objeto **POINT** de
verdad, que PostGIS puede almacenar y consultar espacialmente.

**¿Qué es "estandarización espacial" / WGS84 / EPSG:4326?**
Es asegurar que todas las coordenadas hablen el **mismo idioma geográfico**. WGS84 (código EPSG:4326)
es el sistema de referencia estándar del GPS: latitud y longitud en grados. Estandarizar = garantizar
que todos los puntos estén en ese sistema para que el mapa los ubique bien.

### 4.1 · Qué hacer y decir en pantalla

**Hacer:** Abrir Mage en http://localhost:6789 → menú izquierdo **Pipelines** → clic en `ingesta_vertederos`.

**Decir:**
> "Este es **Mage AI**, nuestro orquestador. Aquí está el pipeline `ingesta_vertederos`. Fíjense en
> la estructura de bloques encadenados: esto es el **DAG**, la secuencia Extract → Transform → Load.
> Cada bloque es un paso independiente que alimenta al siguiente."

**Hacer:** Señalar los tres bloques en el orden del flujo:
1. `extraer_vertederos` (data loader)
2. `transformar_geopandas` (transformer)
3. `cargar_postgis` (data exporter)

**Decir (bloque 1 — Extract):**
> "El primer bloque, `extraer_vertederos`, es el **Extract & Load de datos crudos**: lee el GeoJSON con
> los 261 focos y los guarda tal cual, sin tocar, en una tabla `raw_ingesta`. Así conservamos el dato
> original por trazabilidad, por si algo sale mal en la limpieza."

**Hacer:** Doble clic en el bloque `transformar_geopandas` para mostrar su código.

**Decir (bloque 2 — Transform, el más importante):**
> "El segundo bloque es la **transformación con GeoPandas**, el paso más importante. Aquí hacemos la
> limpieza: eliminamos registros sin coordenadas válidas, quitamos duplicados por código único,
> derivamos la **categoría** de cada foco (Puntos Críticos o Puntos Críticos 2) y —lo clave—
> convertimos cada par longitud/latitud en un objeto geométrico **POINT** en el sistema EPSG:4326.
> Es decir, pasamos de simples números a geometrías que la base espacial entiende."

**Hacer:** Doble clic en `cargar_postgis`.

**Decir (bloque 3 — Load):**
> "El tercer bloque, `cargar_postgis`, toma esas geometrías ya limpias y las **carga en la tabla final**
> de PostgreSQL/PostGIS con un UPSERT, para no duplicar si el punto ya existía. Ese es el destino que
> luego consultan la API y el dashboard."

**Hacer:** Ir al menú **Triggers** (o **Schedules**) del pipeline.

**Decir (automatización — esto lo pide expresamente el rubro):**
> "Y no lo corremos a mano: configuramos un **trigger programado cada 12 horas**. Mage ejecuta el
> pipeline solo, en intervalo, manteniendo el inventario actualizado sin intervención. Eso es la
> **automatización de la orquestación**."

**Hacer (si sobra tiempo — impacta mucho):** Botón **Run@once / Run pipeline** y muestra los bloques
poniéndose en **verde** uno tras otro.

**Decir:**
> "Si lo ejecuto ahora, ven cómo cada bloque corre en orden y se marca en verde: extrae, transforma
> y carga. El pipeline completo funcionando en vivo."

---

# ⭐ PUNTO 5 · Consumo y Visualización (FastAPI + Streamlit) — (5:30–8:00) · **Romeisi** (cierra con Paula)

### 5.0 · Conceptos que debes dominar antes

**¿Qué es una "API REST"?**
Una API es un **mesero entre la base de datos y quien quiere los datos**. El dashboard (o cualquier
programa) le pide datos a la API con una dirección web, y la API va a la base, los busca y se los
devuelve en un formato limpio (JSON). "REST" es solo el estilo estándar de cómo se piden esas cosas
por direcciones web (URLs) usando GET, POST, etc.

**¿Qué es un "endpoint"?**
Es cada **dirección concreta** que ofrece la API, con una función específica. Ejemplos nuestros:
- `GET /locations` → "dame la lista de todos los vertederos".
- `GET /locations/radius` → "dame los vertederos dentro de X metros de este punto".
- `POST /locations` → "registra este nuevo vertedero".
GET = pedir/leer datos; POST = enviar/crear datos.

**¿Qué es FastAPI y Uvicorn?**
**FastAPI** es la librería de Python con la que construimos la API. **Uvicorn** es el "motor" que la
mantiene encendida y escuchando peticiones (el servidor web). Van juntos.

**¿Qué es Swagger / OpenAPI?**
Es una **página de documentación interactiva que FastAPI genera sola**. Lista todos los endpoints y
permite **probarlos con un botón** ahí mismo, sin escribir código. Es lo que abriremos en `/docs`.

**¿Qué es una "consulta espacial" y qué hace `ST_DWithin`?**
Es una pregunta geográfica que resuelve la propia base de datos. `ST_DWithin` es una función de PostGIS
que responde: *"¿qué puntos están a menos de N metros de esta coordenada?"*. Calcula distancias reales
sobre el mapa. Es lo que hace especial a PostGIS frente a una base normal.

**¿Qué es Streamlit y qué significa "consumir la API"?**
**Streamlit** es la librería con la que hicimos el dashboard web. "Consumir la API" significa que el
dashboard **le pide los datos a la API** (no a la base directamente): así respetamos la arquitectura
de capas: base → API → interfaz.

**¿Qué es Folium / el mapa interactivo?**
**Folium** dibuja mapas navegables (zoom, clic) dentro del dashboard. Sobre él pintamos los 261 puntos
como marcadores: eso es "renderizar los objetos geométricos" que menciona el rubro.

### 5.1 · Interacción con la API — Qué hacer y decir

**Hacer:** Abrir http://localhost:8000/docs (Swagger).

**Decir:**
> "La capa de exposición es una API REST en **FastAPI**. Esta página es **Swagger**, la documentación
> que FastAPI genera automáticamente: aquí están todos los endpoints. Tenemos lecturas básicas como
> `GET /locations`, alta de datos con `POST /locations`, y una **consulta espacial**, `GET /locations/radius`."

**Hacer (probar un endpoint en vivo):** Expandir `GET /locations` → *Try it out* → *Execute*.

**Decir:**
> "Si ejecuto `GET /locations`, la API va a PostGIS, trae los vertederos y los devuelve en JSON.
> Estos son los datos reales saliendo de la base a través de la API."

**Hacer (el endpoint espacial, que luce mucho):** Expandir `GET /locations/radius` → *Try it out* →
lat `9.05`, lon `-79.49`, dist `1000` → *Execute*.

**Decir:**
> "Y aquí la consulta espacial: le pido los vertederos a menos de mil metros de este punto. PostGIS,
> con `ST_DWithin`, calcula la distancia real y me devuelve solo esos, ordenados por cercanía. Esto es
> responder una pregunta de negocio directamente con geografía en la base."

### 5.2 · Dashboard + flujo end-to-end — Cierre

**Hacer:** Abrir http://localhost:8501.

**Decir:**
> "Y el cierre: el **dashboard en Streamlit**, que **consume esta API**. En el mapa satelital, hecho con
> **Folium**, se ven los 261 focos de San Miguelito agrupados en clústeres. Debajo está la analítica:
> un **treemap** con la jerarquía por categoría, un **radar** con la distribución por zona geográfica y
> un **mapa de calor** que revela los *hotspots* de concentración."

**Hacer (el momento estrella — demuestra TODO el flujo en vivo):**
1. Pestaña **"Registrar Patacón"** → llenar el formulario con el punto de prueba → *Guardar*.
2. Recargar y mostrar el nuevo punto **apareciendo en el mapa**.

**Decir:**
> "Para demostrar el flujo completo: registro un foco nuevo aquí. El dashboard lo manda por la **API**,
> que lo inserta en **PostGIS** con su geometría, y al recargar **aparece en el mapa**. Ese es el ciclo
> end-to-end: desde el alta en la fuente hasta la visualización final para el usuario de negocio. Gracias."

---

## Preguntas y respuestas (2 min de Q&A)

- **¿Por qué PostGIS y no un PostgreSQL normal?**
  Porque necesitamos geometrías (`POINT`), índice espacial GiST y funciones como `ST_DWithin` para
  búsquedas por radio; con columnas normales eso sería lentísimo o imposible.

- **¿Qué hace exactamente el bloque de GeoPandas?**
  Limpia nulos, deduplica por código único, deriva la categoría y convierte coordenadas en geometrías
  `Point` con CRS EPSG:4326, listas para PostGIS.

- **¿Cómo se automatiza el pipeline?**
  Con un *trigger* programado en Mage cada 12 horas; también se puede lanzar manualmente con *Run*.

- **¿El dashboard lee de la base o de la API?**
  De la **API** (respeta la arquitectura de capas). Si la API estuviera caída, tiene un respaldo que
  lee PostGIS o el GeoJSON directamente.

- **¿Cuál es la fuente y cómo se mantiene dinámica?**
  261 focos de campo del municipio como base; se mantiene viva con el alta de nuevos focos vía
  `POST /locations` desde el dashboard, y el reproceso programado cada 12 h.

- **¿Por qué categoría y no corregimiento?**
  Los datos de campo no traen corregimiento; todos son de San Miguelito. Clasificamos por criticidad
  operativa, que es lo útil para priorizar recolección.

- **¿Es reproducible en otra máquina?**
  Sí: todo está dockerizado, `docker compose up` levanta base, orquestador, API y dashboard idénticos,
  y el esquema SQL se aplica solo al iniciar la base.

---

## Consejos finales

- Hablen **por turnos claros**; el rubro exige que **ambas** demuestren dominio.
- Si algo falla en vivo, mantén la calma y sigue con el siguiente bloque; ten capturas de respaldo.
- No leas de corrido: usa cada pantalla como apoyo y explica **con tus palabras** (por eso están los conceptos de arriba).
- Cierra siempre con el registro en vivo → mapa: es la prueba más contundente del flujo end-to-end.
