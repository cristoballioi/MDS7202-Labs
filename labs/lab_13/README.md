# Laboratorio 13 — Ready, Set, Deploy!

Desde la raíz del laboratorio, instalen las dependencias:

```bash
uv sync --locked --all-groups
```

Este laboratorio necesita **Docker**, que se instala durante la sesión (etapa 0 del
notebook), y una **cuenta de Azure for Students**, que se crea antes. La sección
«Configuración del ambiente» del notebook explica cómo. El despliegue se hace desde el portal de Azure, sin
instalar nada más.

El trabajo se hace en `notebooks/Lab13_Enunciado.ipynb`, en los módulos
marcados como pendientes de `src/aguaapr/` y en los archivos `.env.example`,
`Dockerfile` y `.dockerignore`, que parten como esqueletos
comentados. El resto de `src/aguaapr/` viene implementado y la carpeta `models/`
trae el modelo ya entrenado: este laboratorio no pide entrenar nada. Después de
completar cada etapa, ejecuten:

```bash
uv run pytest -m etapa1
uv run pytest -m etapa2
uv run pytest -m etapa3
uv run pytest -m etapa4
```

La etapa 0 no tiene pruebas. Las demás no necesitan Docker ni una cuenta en la nube. Lo que solo se
comprueba con contenedores o con Azure (la imagen, el contenedor, el despliegue) se
verifica a mano, según indica cada recuadro de comprobación del notebook.

Los datos y su fuente están descritos en `data/raw/README.md`.
