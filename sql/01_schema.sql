-- ============================================================================
-- GEOPataconcitos — Esquema espacial (Etapa 1: DDL PostgreSQL + PostGIS)
-- Base de datos: monitoreo_ambiental  ·  Distrito de San Miguelito, Panamá
-- ----------------------------------------------------------------------------
-- Todos los puntos pertenecen al distrito de San Miguelito.
-- Clasificación operativa: 'Puntos Críticos' y 'Puntos Críticos 2'.
-- SRID 4326 = WGS84 (latitud/longitud GPS).
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS postgis;

-- ----------------------------------------------------------------------------
-- Tabla maestra de vertederos (entidad principal, geometría POINT)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS vertederos_maestro (
    id             SERIAL PRIMARY KEY,
    codigo_unico   VARCHAR(40)  NOT NULL UNIQUE,           -- ej. PAT-00123
    nombre         VARCHAR(200) NOT NULL,
    categoria      VARCHAR(60)  NOT NULL DEFAULT 'Puntos Críticos',
    distrito       VARCHAR(80)  NOT NULL DEFAULT 'San Miguelito',
    ubicacion_fija GEOMETRY(Point, 4326) NOT NULL,
    activo         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_registro TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_vertederos_geom
    ON vertederos_maestro USING GIST (ubicacion_fija);
CREATE INDEX IF NOT EXISTS idx_vertederos_categoria
    ON vertederos_maestro (categoria);

-- ----------------------------------------------------------------------------
-- Tabla RAW (datos crudos tal cual llegan del GeoJSON, antes de transformar)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_ingesta (
    id          SERIAL PRIMARY KEY,
    payload     JSONB NOT NULL,
    lote        VARCHAR(60),
    ingerido_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ----------------------------------------------------------------------------
-- Vista optimizada que consumen la API y el dashboard (aplana geometría)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_vertederos_consumo AS
SELECT
    v.id,
    v.codigo_unico         AS object_id,
    v.nombre               AS name,
    v.categoria,
    v.distrito,
    ST_X(v.ubicacion_fija) AS lon,
    ST_Y(v.ubicacion_fija) AS lat
FROM vertederos_maestro v
WHERE v.activo = TRUE;
