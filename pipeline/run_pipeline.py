from . import extract, transform, load


def main():
    print("=" * 60)
    print(" GEOPataconcitos — Ejecución del pipeline de datos")
    print("=" * 60)

    lote = extract.run()
    gdf = transform.transformar(lote)
    n = load.cargar_final(gdf)

    print("=" * 60)
    print(f" Pipeline completado. {n} vertederos procesados (lote {lote}).")
    print("=" * 60)


if __name__ == "__main__":
    main()
