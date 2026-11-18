"""Configuración del servicio: variables de entorno y archivo `.env`."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración del servicio, leída del entorno con el prefijo `APR_`.

    Si existe un archivo `.env` en la carpeta de trabajo, también se lee de
    ahí; una variable del entorno tiene prioridad sobre el archivo. Una
    variable vacía cuenta como ausente, y las que no están declaradas aquí se
    ignoran.

    | Variable | Campo | Por defecto |
    | --- | --- | --- |
    | `APR_API_KEY` | `api_key`, un `SecretStr` | obligatoria |
    | `APR_GRUPO` | `grupo` | obligatoria |
    | `APR_MODEL_DIR` | `model_dir` | `models` (como `Path`) |
    | `APR_LOG_LEVEL` | `log_level` | `INFO` |
    """

    # Su código aquí: declaren `model_config` y los cuatro campos de la tabla.


@lru_cache
def get_settings() -> Settings:
    """Lee la configuración una sola vez y la reutiliza."""
    # Los campos obligatorios los completa el entorno al crear `Settings`; el
    # verificador de tipos no lo ve.
    return Settings()  # pyright: ignore[reportCallIssue]
