"""DB-URL erstellen."""

import ssl  # nach oben verschieben
from importlib.resources import files
from importlib.resources.abc import Traversable
from typing import Final, Literal

from loguru import logger
from sqlalchemy.engine import URL

from inventory.config.config import inventory_config, resources_path


__all__ = [
    "db_connect_args",
    "db_dialect",
    "db_log_statements",
    "db_url",
    "db_url_admin",
]

_db_toml: Final = inventory_config.get("db", {})

db_dialect: Final[Literal["postgresql", "mysql", "sqlite"]] = _db_toml.get(
    "dialect",
    "postgresql",
)
"""DB-Dialekt für SQLAlchemy: 'postgresql', 'mysql', 'sqlite'."""
logger.debug("db: db_dialect={}", db_dialect)

name: Final[str] = _db_toml.get("name", "inventory")
_main_memory: Final[bool] = bool(_db_toml.get("main-memory", False))
_host: Final[str] = _db_toml.get("host", db_dialect)
_db_host: Final[str] = _host
_username: Final[str] = _db_toml.get("username", "inventory")
_password: Final[str] = _db_toml.get("password", "Change Me!")
_password_admin: Final[str] = _db_toml.get("password-admin", "Change Me!")

db_log_statements: Final[bool] = bool(_db_toml.get("log-statements", False))
"""True, falls die SQL-Anweisungen protokolliert werden sollen."""


__db_resources_traversable: Final[Traversable] = files(resources_path)

def _get_drivername() -> str:
    return "mysql+aiomysql"

def _get_database() -> str:
    return name

def _create_db_url() -> URL:
        return URL.create(
            drivername=_get_drivername(),
            username=_username,
            password=_password,
            host=_db_host,
            database=_get_database(),
        )

def _create_db_url_admin() -> URL:
        return URL.create(
            drivername=_get_drivername(),
            username="root",
            password=_password_admin,
            host=_db_host,
            database=_get_database(),
        )


db_url: Final[URL] = _create_db_url()
"""DB-URL für SQLAlchemy."""
logger.debug("db: db_url={}", db_url)

db_url_admin: Final[URL] = _create_db_url_admin()
"""DB-URL für den Superuser für SQLAlchemy."""

def _create_connect_args() -> dict[str, object] | None:
    verify_cert: Final[bool] = False

    if not verify_cert:
        logger.warning("Zertifikatsprüfung ist deaktiviert (nur für DEV empfohlen!)")
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return {"ssl": context}  # ✅ SSLContext statt dict

    cafile: Final = str(__db_resources_traversable / db_dialect / "certificate.crt")
    context = ssl.create_default_context(cafile=cafile)
    return {"ssl": context}


# db_connect_args: dict[str, str | dict[str, str]] | None = _create_connect_args()
db_connect_args = None
"""Schlüssel-Wert-Paare für TLS bei PostgreSQL oder MySQL."""
logger.debug("db: db_connect_args={}", db_connect_args)
