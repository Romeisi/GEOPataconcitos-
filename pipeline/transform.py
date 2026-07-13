import json

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from .config import DB_CONFIG

CORREGIMIENTOS_VALIDOS = {
    "Amelia Denis de Icaza", "Belisario Porras", "José Domingo Espinar",
    "Mateo Iturralde", "Victoriano Lorenzo", "Arnulfo Arias",
    "Belisario Frías", "Omar Torrijos", "Rufina Alfaro",
}


def categoria_desde_folder(folder: str) -> str:
    folder = folder or ""
    if "Puntos Críticos 2" in folder or "Puntos Criticos 2" in folder:
        return "Puntos Críticos 2"
    return "Puntos Críticos"


def _leer_lote_raw(lote):
    import psycopg2
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            if lote:
                cur.execute("SELECT payload FROM raw_ingesta WHERE lote = %s;", (lote,))
            else:
                cur.execute("""
                    SELECT payload FROM raw_ingesta
                    WHERE lote = (SELECT lote FROM raw_ingesta ORDER BY ingerido_en DESC LIMIT 1);
                """)
            filas = [r[0] for r in cur.fetchall()]
    finally:
        conn.close()
    return [f if isinstance(f, dict) else json.loads(f) for f in filas]


def transformar(lote=None) -> gpd.GeoDataFrame:
    features = _leer_lote_raw(lote)
    registros = []
    for feat in features:
        geom = feat.get("geometry", {}) or {}
        prop = feat.get("properties", {}) or {}
        if geom.get("type") != "Point":
            continue
        coords = geom.get("coordinates")
        if not coords or len(coords) < 2:
            continue

        lon, lat = float(coords[0]), float(coords[1])
        oid = prop.get("OBJECTID") or prop.get("codigo_unico") or len(registros) + 1
        codigo = prop.get("codigo_unico") or f"PAT-{int(oid):05d}"
        nombre = (prop.get("Name") or prop.get("name") or "Punto Crítico").strip() or "Punto Crítico"
        categoria = categoria_desde_folder(prop.get("FolderPath", ""))

        registros.append({
            "codigo_unico": codigo,
            "nombre": nombre,
            "categoria": categoria,
            "lon": lon, "lat": lat,
            "geometry": Point(lon, lat),
        })

    df = pd.DataFrame(registros).drop_duplicates(subset=["codigo_unico"])
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
    print(f"[TRANSFORM] {len(gdf)} registros limpios y georreferenciados (EPSG:4326)")
    return gdf


if __name__ == "__main__":
    transformar()
