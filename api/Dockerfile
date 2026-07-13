FROM python:3.11-slim

# Dependencias del sistema para geopandas/shapely (GEOS, GDAL, PROJ)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgeos-dev libgdal-dev libproj-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/
COPY pipeline/ ./pipeline/

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
