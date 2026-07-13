
import sys
sys.path.append("/home/src")

import geopandas as gpd  # noqa: E402
from shapely import wkt  # noqa: E402

from pipeline import load  # noqa: E402

if "data_exporter" not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def exportar_a_postgis(data, *args, **kwargs):
    df = data.copy()
    df["geometry"] = df["wkt"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
    n = load.cargar_final(gdf)
    print(f"[MAGE-EXPORTER] {n} vertederos cargados en monitoreo_ambiental")
