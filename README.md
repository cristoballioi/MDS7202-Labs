# MDS7202 - Laboratorio de Programación Científica para Ciencia de Datos

Repositorio del curso MDS7202 (Otoño 2026), Facultad de Ciencias Físicas y Matemáticas, Universidad de Chile.

## Integrantes

| Nombre | GitHub |
|--------|--------|
| Cristóbal Lioi | [@cristoballioi](https://github.com/cristoballioi) |
| Julio Badilla | [@jbadilla10](https://github.com/jbadilla10) |

## Estructura del repositorio

.
├── .github/
│   ├── workflows/
│   │   └── lint.yml
│   └── pull_request_template.md
├── labs/
│   ├── lab_1/
│   └── ...
├── pyproject.toml
├── .github/
├── .pre-commit-config.yaml
└── README.md

## Configuración del entorno

uv sync --locked --all-groups
uv run pre-commit install
```
