import json
import uuid
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import Json

from .config import DB_CONFIG, SEED_GEOJSON_PATH


def extraer_features(ruta: str = SEED_GEOJSON_PATH) -> list:
    with open(ruta, "r", encoding="utf-8") as f:
        data = json.load(f)
    features = data.get("features", [])
    print(f"[EXTRACT] {len(features)} features leídos de {ruta}")
    return features


def cargar_raw(features: list) -> str:
    lote = f"lote_{datetime.now(timezone.utc):%Y%m%d%H%M%S}_{uuid.uuid4().hex[:6]}"
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn, conn.cursor() as cur:
            for feat in features:
                cur.execute(
                    "INSERT INTO raw_ingesta (payload, lote) VALUES (%s, %s);",
                    (Json(feat), lote),
                )
        print(f"[LOAD-RAW] {len(features)} registros crudos cargados en lote '{lote}'")
    finally:
        conn.close()
    return lote


def run(ruta: str = SEED_GEOJSON_PATH) -> str:
    features = extraer_features(ruta)
    return cargar_raw(features)


if __name__ == "__main__":
    run()
