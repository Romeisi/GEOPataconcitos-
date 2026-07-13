from pydantic import BaseModel, Field

CATEGORIAS = ("Puntos Críticos", "Puntos Críticos 2")


class Location(BaseModel):
    object_id: str = Field(..., description="Código único del vertedero (ej. PAT-00123)")
    name: str = Field(..., description="Nombre oficial de campo")
    categoria: str = Field("Puntos Críticos", description="Clasificación operativa")
    distrito: str = Field("San Miguelito", description="Distrito")
    lon: float = Field(..., description="Longitud (WGS84)")
    lat: float = Field(..., description="Latitud (WGS84)")


class LocationRadius(Location):
    distancia_m: float = Field(..., description="Distancia al punto de consulta, en metros")


class LocationCreate(BaseModel):
    codigo_unico: str | None = Field(
        None, description="Código único (opcional; se autogenera PAT-XXXXX si se omite)")
    nombre: str = Field(..., min_length=2, description="Nombre oficial de campo")
    categoria: str = Field("Puntos Críticos", description="Clasificación operativa")
    lat: float = Field(..., ge=-90, le=90, description="Latitud (WGS84)")
    lon: float = Field(..., ge=-180, le=180, description="Longitud (WGS84)")


class CategoriaStat(BaseModel):
    categoria: str
    cantidad: int


class Health(BaseModel):
    status: str
    database: str
    total_vertederos: int
