import json
import os

try:
    with open('.chalice/config.json') as _config_json_content:
        _config_json = json.load(_config_json_content)
except FileNotFoundError:
    pass


def read_environ_var(key: str) -> str:
    if key in os.environ:
        return os.environ[key]
    return str(_config_json['environment_variables'][key])
