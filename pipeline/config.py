import os

DB_CONFIG = {
    "host":     os.getenv("POSTGRES_HOST", "localhost"),
    "port":     os.getenv("POSTGRES_PORT", "5432"),
    "dbname":   os.getenv("POSTGRES_DB", "monitoreo_ambiental"),
    "user":     os.getenv("POSTGRES_USER", "romeisi"),
    "password": os.getenv("POSTGRES_PASSWORD", "ola123"),
}

SEED_GEOJSON_PATH = os.getenv(
    "SEED_GEOJSON_PATH",
    os.path.join(os.path.dirname(__file__), "data", "patacones_coordenadas.geojson"),
)


def sqlalchemy_url() -> str:
    c = DB_CONFIG
    return f"postgresql+psycopg2://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['dbname']}"


def get_engine():
    from sqlalchemy import create_engine
    return create_engine(sqlalchemy_url(), pool_pre_ping=True)
