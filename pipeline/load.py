import geopandas as gpd
import psycopg2

from .config import DB_CONFIG


def cargar_final(gdf: gpd.GeoDataFrame) -> int:
    conn = psycopg2.connect(**DB_CONFIG)
    n = 0
    try:
        with conn, conn.cursor() as cur:
            for _, r in gdf.iterrows():
                cur.execute(
                    """
                    INSERT INTO vertederos_maestro
                        (codigo_unico, nombre, categoria, ubicacion_fija, activo)
                    VALUES
                        (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), TRUE)
                    ON CONFLICT (codigo_unico) DO UPDATE
                        SET nombre = EXCLUDED.nombre,
                            categoria = EXCLUDED.categoria,
                            ubicacion_fija = EXCLUDED.ubicacion_fija,
                            activo = TRUE;
                    """,
                    (r["codigo_unico"], r["nombre"], r["categoria"], r["lon"], r["lat"]),
                )
                n += 1
        print(f"[LOAD] {n} vertederos cargados/actualizados en la tabla final")
    finally:
        conn.close()
    return n


if __name__ == "__main__":
    from .transform import transformar
    cargar_final(transformar())
