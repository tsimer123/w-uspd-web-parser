from os import path

import yaml


def get_data() -> dict | None:
    file_path = 'config.yml'
    if path.isfile(file_path) is True:
        with open(file_path) as file:
            date = yaml.safe_load(file)
            return date
    else:
        return None


def get_log_state_db() -> int | None:
    result = get_data()
    if result is not None:
        if 'logging' in result and 'state_db' in result['logging']:
            if type(result['logging']['state_db']) is int:
                return result['logging']['state_db']
            else:
                return None
        else:
            return None
    else:
        return None


def get_db_name() -> str | None:
    result = get_data()
    if result is not None:
        if 'db' in result and 'db_name' in result['db']:
            if type(result['db']['db_name']) is str:
                return result['db']['db_name']
            else:
                return None
        else:
            return None
    else:
        return None


def get_time_restart_true_task() -> int | None:
    result = get_data()
    if result is not None:
        if 'request' in result and 'time_restart_true_task' in result['request']:
            if type(result['request']['time_restart_true_task']) is int:
                return result['request']['time_restart_true_task']
            else:
                return None
        else:
            return None
    else:
        return None
