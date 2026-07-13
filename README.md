# GEOPataconcitos — Arquitectura y Exposición de Datos Geoespaciales

Flujo de datos End-to-End para el inventario y monitoreo georreferenciado de vertederos
informales de basura ("pataconcitos") en el Distrito de San Miguelito, Panamá.

**Autoras:** Romeisi Paniagua & Paula Ramos · Tópicos Especiales II · 2026

---

## Arquitectura

```
GeoJSON (fuente)  ──►  Pipeline Python / Mage AI  ──►  PostgreSQL + PostGIS  ──►  FastAPI  ──►  Streamlit
   Extract               Transform (GeoPandas)          monitoreo_ambiental       API REST      Dashboard
```

Cada componente corre en un contenedor orquestado por `docker-compose`.

| Servicio      | Descripción                                   | Puerto |
|---------------|-----------------------------------------------|--------|
| `db`          | PostgreSQL 16 + PostGIS 3.4                    | 5432   |
| `mage`        | Orquestador Mage AI (pipeline programado 12h) | 6789   |
| `api`         | FastAPI + Uvicorn (capa de exposición)        | 8000   |
| `dashboard`   | Streamlit (capa de consumo)                   | 8501   |

---

## Estructura del repositorio

```
geopataconcitos/
├── docker-compose.yml            # Orquestación de todos los servicios
├── .env.example                  # Variables de entorno (copiar a .env)
├── requirements.txt              # Dependencias Python
├── sql/
│   └── 01_schema.sql             # DDL PostGIS (Etapa 1)
├── docs/
│   ├── especificacion_tecnica.md # Documento de especificación (Etapa 1)
│   └── arquitectura.drawio       # Diagrama de arquitectura (Draw.io)
├── pipeline/
│   ├── config.py                 # Configuración / conexión
│   ├── extract.py                # Extract & Load raw (Etapa 2)
│   ├── transform.py              # Transform con GeoPandas (Etapa 2)
│   ├── load.py                   # Carga tabla final optimizada
│   ├── run_pipeline.py           # Orquestador local (E-T-L completo)
│   └── data/
│       └── vertederos_seed.geojson
├── mage/geopataconcitos/         # Bloques del pipeline en Mage AI
│   ├── data_loaders/extraer_vertederos.py
│   ├── transformers/transformar_geopandas.py
│   └── data_exporters/cargar_postgis.py
├── api/
│   ├── main.py                   # App FastAPI (Etapa 3)
│   ├── database.py               # Pool de conexión
│   ├── schemas.py                # Modelos Pydantic
│   └── Dockerfile
└── dashboard/
    ├── dashboard_geopataconcitos.py
    └── Dockerfile
```

---

## Puesta en marcha (reproducible)

```bash
# 1. Clonar y configurar
cp .env.example .env

# 2. Levantar toda la infraestructura
docker compose up -d --build

# 3. Cargar el esquema y correr el pipeline por primera vez
docker compose exec api python -m pipeline.run_pipeline   # o desde Mage

# 4. Abrir en el navegador
#    Dashboard:      http://localhost:8501
#    API (Swagger):  http://localhost:8000/docs
#    Mage AI:        http://localhost:6789
```

> El esquema SQL (`sql/01_schema.sql`) se aplica automáticamente al inicializar el
> contenedor de PostgreSQL gracias al volumen `docker-entrypoint-initdb.d`.

---

## Endpoints principales de la API

| Método | Ruta                                          | Descripción                                        |
|--------|-----------------------------------------------|----------------------------------------------------|
| GET    | `/health`                                     | Estado del servicio y de la base de datos          |
| GET    | `/locations`                                  | Lista todos los vertederos (con filtros opcionales)|
| POST   | `/locations`                                  | Registra un nuevo patacón (alta manual del usuario)|
| GET    | `/locations/geojson`                          | FeatureCollection GeoJSON generado con `ST_AsGeoJSON` |
| GET    | `/locations/{object_id}`                      | Detalle de un vertedero                            |
| GET    | `/locations/radius?lat=X&lon=Y&dist=1000`     | Vertederos dentro de un radio (metros) — `ST_DWithin` |
| GET    | `/stats/categoria`                            | Agregados por categoría para el dashboard          |

> **Datos:** 261 focos, todos en el distrito de San Miguelito, clasificados en
> "Puntos Críticos" y "Puntos Críticos 2". El inventario inicial se carga una vez desde
> `patacones_coordenadas.geojson` con el pipeline; a partir de ahí los usuarios **agregan
> nuevos patacones** mediante `POST /locations` (pestaña "Registrar Patacón" del dashboard).

Documentación interactiva (Swagger/OpenAPI) autogenerada en `/docs`.
