import os
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

DB_CONFIG = {
    "host":     os.getenv("POSTGRES_HOST", "localhost"),
    "port":     os.getenv("POSTGRES_PORT", "5432"),
    "dbname":   os.getenv("POSTGRES_DB", "monitoreo_ambiental"),
    "user":     os.getenv("POSTGRES_USER", "romeisi"),
    "password": os.getenv("POSTGRES_PASSWORD", "ola123"),
}

_pool = None


def init_pool():
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(minconn=1, maxconn=10, **DB_CONFIG)
    return _pool


def close_pool():
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None


@contextmanager
def get_cursor():
    pool = init_pool()
    conn = pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
        conn.commit()
    finally:
        pool.putconn(conn)
