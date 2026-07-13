# Documento de Especificación Técnica — GEOPataconcitos

**Proyecto:** Arquitectura y Exposición de Datos Geoespaciales
**Caso de uso:** Inventario y monitoreo de vertederos informales de basura ("pataconcitos") en el Distrito de San Miguelito, Panamá
**Autoras:** Romeisi Paniagua & Paula Ramos
**Curso:** Tópicos Especiales II — 2026

---

## 1. Objetivo

Diseñar, orquestar y desplegar un flujo de datos End-to-End que integre una fuente de datos georreferenciada y la exponga a través de un microservicio (API REST) y un dashboard interactivo, aplicando buenas prácticas de ingeniería de software, modelado espacial y contenedorización.

## 2. Selección del caso de uso

Se monitorean **botaderos informales** detectados sobre imágenes satelitales (resolución 10 m, Sentinel-2) en los 9 corregimientos de San Miguelito. Cada foco posee coordenadas (latitud/longitud) y un área estimada. La capa se **actualiza periódicamente** (cada corrida del pipeline registra una nueva detección), lo que aporta el componente dinámico y de serie temporal.

## 3. Requerimientos

### 3.1 Funcionales
- Ingerir la fuente de datos georreferenciada y almacenar los datos crudos.
- Limpiar, imputar nulos y convertir coordenadas a geometrías `POINT` (EPSG:4326).
- Persistir en una base espacial y exponer consultas por atributos y por radio.
- Visualizar los focos en un mapa satelital y en gráficos analíticos.
- Permitir la descarga del inventario en CSV.

### 3.2 No funcionales
- **Reproducibilidad:** todo el stack se levanta con `docker compose up`.
- **Rendimiento espacial:** índice GiST sobre la geometría; consultas por radio con `ST_DWithin`.
- **Automatización:** pipeline programado cada 12 horas mediante Mage AI.
- **Documentación:** API autodocumentada con Swagger/OpenAPI.

## 4. Stack tecnológico

| Capa            | Tecnología                         |
|-----------------|------------------------------------|
| Orquestación    | Mage AI                            |
| Almacenamiento  | PostgreSQL 16 + PostGIS 3.4        |
| Procesamiento   | Python 3.11 · Pandas · GeoPandas   |
| Backend / API   | FastAPI + Uvicorn                  |
| Visualización   | Streamlit · Folium · Plotly        |
| Infraestructura | Docker + Docker Compose            |

## 5. Arquitectura

```
GeoJSON (fuente) ─► Extract&Load ─► raw_ingesta ─► Transform (GeoPandas)
                                                        │
                                    Load final ─► vertederos_maestro + detecciones_historial
                                                        │
                             FastAPI (/locations, /locations/radius) ─► Streamlit (mapa + analítica)
```

El orquestador (Mage AI) dispara el flujo Extract → Transform → Load cada 12 horas. Ver diagrama completo en `arquitectura.drawio`.

## 6. Modelo Entidad-Relación (ERD)

Todos los focos pertenecen al distrito de San Miguelito; la dimensión de análisis es la **categoría operativa** (`Puntos Críticos` / `Puntos Críticos 2`), derivada del `FolderPath` del origen.

```
vertederos_maestro
  id PK · codigo_unico UNIQUE · nombre · categoria · distrito
  ubicacion_fija GEOMETRY(Point,4326) · activo · fecha_registro

raw_ingesta
  id PK · payload JSONB · lote · ingerido_en
```

### 6.1 Decisiones de modelado
- **Tipos espaciales:** `ubicacion_fija` es `GEOMETRY(Point, 4326)` (WGS84). Para distancias reales en metros se castea a `geography` en las consultas por radio.
- **Categoría en lugar de corregimiento:** el dataset no contiene división por corregimiento; se clasifica por criticidad operativa, útil para priorizar recolección.
- **Zona geográfica derivada:** el dashboard calcula en tiempo de consulta una rosa de 8 sectores (Norte, Noreste, …) desde el centroide, para el gráfico de radar, sin persistirla.
- **Datos crudos:** `raw_ingesta` conserva el GeoJSON original en `JSONB` antes de transformar (trazabilidad).
- **Idempotencia:** la carga hace `UPSERT` por `codigo_unico`.

## 7. Índices
- `idx_vertederos_geom` — GiST sobre `ubicacion_fija` (consultas espaciales).
- `idx_vertederos_categoria` — filtros por categoría.

## 8. Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado del servicio y de la BD |
| GET | `/locations` | Lista de vertederos (filtro + paginación) |
| GET | `/locations/{object_id}` | Detalle de un vertedero |
| GET | `/locations/radius?lat=&lon=&dist=` | Búsqueda espacial por radio (`ST_DWithin`) |
| GET | `/stats/corregimiento` | Agregados por corregimiento |

## 9. Puesta en marcha

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec api python -m pipeline.run_pipeline
# Dashboard: http://localhost:8501 · API: http://localhost:8000/docs · Mage: http://localhost:6789
```
