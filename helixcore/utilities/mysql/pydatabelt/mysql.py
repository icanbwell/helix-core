import os
import structlog
from typing import Dict, Any, Optional, List, Set

from helixcore.utilities.aws_helpers.ssm_helper import (
    get_ssm_config_with_env_var,
)

logger = structlog.get_logger(__name__)

CONNECTION_CONFIG_KEYS: Set[str] = {
    "username",
    "password",
    "db",
    "host",
    "port",
}


def _remove_excess_config_keys(config: Dict[str, Any]) -> None:
    for key in list(config.keys()):
        if key not in CONNECTION_CONFIG_KEYS:
            del config[key]


def _get_mysql_config_from_aws_ssm(
    db_name: str,
    env: str,
    truncate_keys: bool = True,
    default_schema: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Gets the MySql config from AWS SSM
    :param db_name: MySQL database name
    :param env: Environment (local, dev, prod, ...) passed in by caller of get_mysql_config()
    :param truncate_keys: Whether get ssm_config() should truncate the keys. Default here is True.
    :param default_schema: Default db schema
    :return Parameter Store config
    """
    path: str = f"/databelt/dbs/{db_name}/"

    config: Dict[str, Any] = get_ssm_config_with_env_var(
        path=path, env=env, truncate_keys=truncate_keys, progress_logger=logger
    )

    config["username"] = config.get("credentials/default/username")
    config["password"] = config.get("credentials/default/password")
    config_default_schema: Optional[str] = config.get("default-schema") or config.get(
        "default-db"
    )
    config["db"] = default_schema or config_default_schema
    _remove_excess_config_keys(config)
    return config


def _get_mysql_config_from_environment_variables(
    db_name: str, default_schema: Optional[str] = None
) -> Dict[str, Any]:
    """
    Reads environment variables to set the config to connect to MySql
    """
    config: Dict[str, Any] = {}

    _get_or_override_mysql_config_from_environment_variables(
        config=config, default_schema=default_schema, db_name=db_name
    )

    _remove_excess_config_keys(config)
    return config


def _get_or_override_mysql_config_from_environment_variables(
    config: Dict[str, Any], default_schema: Optional[str], db_name: str
) -> Dict[str, Any]:
    prefix: str = "{}_DB_".format(db_name.upper())
    for key in CONNECTION_CONFIG_KEYS:
        env_var_name: str = f"{prefix}{key}".upper()
        env_var_value: Optional[str] = os.getenv(env_var_name)

        if (
            env_var_value is None
        ):  # Explicitly check for None, since a user could set an env var to the empty string
            if key not in config:
                logger.warn(
                    "No matching environment variable found",
                    key=key,
                    env_var=env_var_name,
                )
        else:
            config[key] = env_var_value
    if default_schema:
        config["db"] = default_schema

    return config


def get_mysql_config(
    db_name: str, env: Optional[str] = None, default_schema: Optional[str] = None
) -> Dict[str, Any]:
    """
    Returns a dict containing connection information for the given database and environment.

    If no environment is passed in, defaults to using the environment specified in an environment variable, or "prod" if
    no such environment variable exists.

    Allows overriding of SSM values using environment variables
    """
    env_str: str
    if env is None:
        env_str = os.getenv("ENV", "prod")
    else:
        env_str = str(env)

    mysql_config: Dict[str, Any]
    if env == "local":
        mysql_config = _get_mysql_config_from_environment_variables(
            db_name, default_schema=default_schema
        )
    else:
        mysql_config = _get_mysql_config_from_aws_ssm(
            db_name, env_str, default_schema=default_schema
        )
        # allow override of SSM values by environment variables
        mysql_config = _get_or_override_mysql_config_from_environment_variables(
            config=mysql_config, default_schema=default_schema, db_name=db_name
        )

    return mysql_config


def construct_mysql_connection_string(
    host: Optional[str] = None,
    port: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    db: Optional[str] = None,
    protocol: str = "mysql+pymysql",
    params: Optional[Dict[str, str]] = None,
) -> str:
    """
    Uses the parameters to construct a mysql connection string
    """
    conn_str: str = f"{protocol}://{username}:{password}@{host}:{port}"

    if db is not None:
        conn_str = f"{conn_str}/{db}"

    if params:
        params_list: List[str] = [f"{k}={v}" for k, v in params.items()]
        params_string: str = "&".join(params_list)
        conn_str = f"{conn_str}?{params_string}"

    return conn_str
