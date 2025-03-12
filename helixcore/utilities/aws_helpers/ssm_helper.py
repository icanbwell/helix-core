from typing import Dict, Any

from helixcore.utilities.aws.config import get_ssm_config
import os
from helixcore.progress_logger.progress_logger import ProgressLogger
from helixcore.logger.log_level import LogLevel


def get_ssm_param_with_env_var(
    path: str,
    ssm_param: str,
    progress_logger: ProgressLogger,
) -> str:
    """
    Query AWS Systems Manager Parameter Store for a specific path and parameter.

    :param path: Path to parameter in Parameter Store WITHOUT the root environment (e.g. "helix/integrations/api-keys/lee/md_staff")
    :param ssm_param: Specific name of parameter in Parameter Store (e.g. "client_secret")
    :param progress_logger: Progress Logger object for logging behavior
    :return string of value stored in Parameter Store
    """

    bwell_env = os.environ.get("BWELL_ENV", "local")
    env = os.environ.get("ENV", "local")

    # Just in case a path or parameter is sent with a leading '/'
    if path[0] == "/":
        path = path[1:]
    if path[-1] == "/":
        path = path[:-1]
    if ssm_param[0] == "/":
        ssm_param = ssm_param[1:]

    try:
        ssm_path = f"/{env}/{path}"
        return str(get_ssm_config(path=ssm_path).get(f"{ssm_path}/{ssm_param}"))
    except Exception:
        progress_logger.write_to_log(
            name="Get SSM Param",
            message=f"Root ENV not found; attempting BWELL_ENV. Verify your param exists with root of '/{env}' or '/{bwell_env}'",
            log_level=LogLevel.INFO,
        )
        ssm_path = f"/{bwell_env}/{path}"
        return str(get_ssm_config(path=ssm_path).get(f"{ssm_path}/{ssm_param}"))


def get_ssm_config_with_env_var(
    path: str,
    env: str,
    progress_logger: ProgressLogger,
    truncate_keys: bool = False,
) -> Dict[str, Any]:
    """
    Get AWS Systems Manager Parameter Store for a specific path.

    :param path: Path to Parameter Store WITHOUT the root environment (e.g. "helix/integrations/api-keys/lee/md_staff")
    :param env: Legacy env passed in by caller (prod, client-sandbox, staging, dev, local)
    :param progress_logger: Progress Logger object for logging behavior
    :param truncate_keys: Whether get_ssm_config() should truncate the keys.  Its default is False.
    :return Parameter Store config
    """

    # In case a path is sent with a leading '/'
    if path[0] == "/":
        path = path[1:]

    try:
        ssm_path = f"/{env}/{path}"
        return get_ssm_config(path=ssm_path, truncate_keys=truncate_keys)
    except Exception:
        # Newly defined environment path. (prod-ue1, client-sandbox-ue1, etc.)
        bwell_env = os.environ.get("BWELL_ENV", env)

        progress_logger.write_to_log(
            name="Get SSM Config",
            message=f"Root ENV not found; attempting BWELL_ENV. Verify your param exists with root of '/{env}' or '/{bwell_env}'",
            log_level=LogLevel.INFO,
        )
        ssm_path = f"/{bwell_env}/{path}"
        return get_ssm_config(path=ssm_path, truncate_keys=truncate_keys)
