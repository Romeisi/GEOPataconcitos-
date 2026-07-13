
import sys
sys.path.append("/home/src")  # ruta del proyecto montado en el contenedor de Mage

from pipeline import extract  # noqa: E402

if "data_loader" not in globals():
    from mage_ai.data_preparation.decorators import data_loader


@data_loader
def cargar_datos_crudos(*args, **kwargs):
    lote = extract.run()
    return {"lote": lote}


@test
def test_output(output, *args) -> None:
    assert output is not None, "El data loader no devolvió el id del lote"
    assert "lote" in output, "Falta la clave 'lote' en la salida"
