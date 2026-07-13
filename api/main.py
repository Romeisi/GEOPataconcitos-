from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from .database import init_pool, close_pool, get_cursor
from .schemas import Location, LocationRadius, LocationCreate, CategoriaStat, Health


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_pool()
    yield
    close_pool()


app = FastAPI(
    title="GEOPataconcitos API",
    description="Servicio de exposición de datos geoespaciales de vertederos "
                "informales del Distrito de San Miguelito, Panamá.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


@app.get("/health", response_model=Health, tags=["Sistema"])
def health():
    try:
        with get_cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM vertederos_maestro WHERE activo = TRUE;")
            n = cur.fetchone()["n"]
        return Health(status="ok", database="conectada", total_vertederos=n)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Base de datos no disponible: {e}")


@app.get("/locations", response_model=list[Location], tags=["Vertederos"])
def listar_locations(
    categoria: str | None = Query(None, description="Filtra por categoría"),
    limit: int = Query(1000, ge=1, le=5000),
    offset: int = Query(0, ge=0),
):
    sql = """
        SELECT object_id, name, categoria, distrito, lon, lat
        FROM v_vertederos_consumo
        WHERE (%(cat)s IS NULL OR categoria = %(cat)s)
        ORDER BY object_id
        LIMIT %(limit)s OFFSET %(offset)s;
    """
    with get_cursor() as cur:
        cur.execute(sql, {"cat": categoria, "limit": limit, "offset": offset})
        return cur.fetchall()


@app.post("/locations", response_model=Location, status_code=status.HTTP_201_CREATED, tags=["Vertederos"])
def crear_location(nuevo: LocationCreate):
    with get_cursor() as cur:
        codigo = nuevo.codigo_unico
        if not codigo:
            cur.execute("SELECT COALESCE(MAX(id), 0) + 1 AS siguiente FROM vertederos_maestro;")
            codigo = f"PAT-{cur.fetchone()['siguiente']:05d}"

        cur.execute("SELECT 1 FROM vertederos_maestro WHERE codigo_unico = %s;", (codigo,))
        if cur.fetchone():
            raise HTTPException(status_code=409, detail=f"El código '{codigo}' ya existe")

        cur.execute(
            """
            INSERT INTO vertederos_maestro
                (codigo_unico, nombre, categoria, ubicacion_fija, activo)
            VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), TRUE);
            """,
            (codigo, nuevo.nombre, nuevo.categoria, nuevo.lon, nuevo.lat),
        )

    return Location(
        object_id=codigo, name=nuevo.nombre, categoria=nuevo.categoria,
        distrito="San Miguelito", lon=nuevo.lon, lat=nuevo.lat,
    )


@app.get("/locations/geojson", tags=["Vertederos"])
def locations_geojson(categoria: str | None = Query(None)):
    sql = """
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', COALESCE(json_agg(
                json_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(v.ubicacion_fija)::json,
                    'properties', json_build_object(
                        'codigo_unico', v.codigo_unico,
                        'name', v.nombre,
                        'categoria', v.categoria
                    )
                )
            ), '[]'::json)
        ) AS fc
        FROM vertederos_maestro v
        WHERE v.activo = TRUE
          AND (%(cat)s IS NULL OR v.categoria = %(cat)s);
    """
    with get_cursor() as cur:
        cur.execute(sql, {"cat": categoria})
        return cur.fetchone()["fc"]


@app.get("/locations/radius", response_model=list[LocationRadius], tags=["Consultas espaciales"])
def locations_por_radio(
    lat: float = Query(..., description="Latitud del punto de consulta (WGS84)"),
    lon: float = Query(..., description="Longitud del punto de consulta (WGS84)"),
    dist: float = Query(1000, gt=0, description="Radio de búsqueda en metros"),
):
    sql = """
        SELECT
            v.codigo_unico AS object_id,
            v.nombre       AS name,
            v.categoria,
            v.distrito,
            ST_X(v.ubicacion_fija) AS lon,
            ST_Y(v.ubicacion_fija) AS lat,
            ST_Distance(v.ubicacion_fija::geography,
                        ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)::geography) AS distancia_m
        FROM vertederos_maestro v
        WHERE v.activo = TRUE
          AND ST_DWithin(
                v.ubicacion_fija::geography,
                ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)::geography,
                %(dist)s)
        ORDER BY distancia_m ASC;
    """
    with get_cursor() as cur:
        cur.execute(sql, {"lat": lat, "lon": lon, "dist": dist})
        return cur.fetchall()


@app.get("/locations/{object_id}", response_model=Location, tags=["Vertederos"])
def obtener_location(object_id: str):
    with get_cursor() as cur:
        cur.execute(
            "SELECT object_id, name, categoria, distrito, lon, lat "
            "FROM v_vertederos_consumo WHERE object_id = %s;",
            (object_id,),
        )
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Vertedero '{object_id}' no encontrado")
    return row


@app.get("/stats/categoria", response_model=list[CategoriaStat], tags=["Estadísticas"])
def stats_por_categoria():
    sql = """
        SELECT categoria, COUNT(*)::int AS cantidad
        FROM v_vertederos_consumo
        GROUP BY categoria
        ORDER BY cantidad DESC;
    """
    with get_cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


@app.get("/", tags=["Sistema"])
def root():
    return {"servicio": "GEOPataconcitos API", "docs": "/docs", "version": "2.0.0"}
