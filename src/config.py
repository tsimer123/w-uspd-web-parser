from hand_config.parse_config import get_db_name, get_log_state_db, get_time_restart_true_task

user_agent = (
    'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
)

# имя БД
# db_name = 'sqlite_python_alchemy.db'

# время ожидания статуса wait для get_shedule в секундах
timeout_task = {
    'get_wl': 1800,
    'get_messages': 1800,
    'get_messages_bs': 3600,
}

# перечень команд для функции get_command
list_command = [
    'get_wl',
    'get_messages',
    'get_messages_bs',
]

list_msg_command = [
    'get_messages',
    'get_messages_bs',
]

# время перезапуска true тасок
_time_restart_true_task = get_time_restart_true_task()
time_restart_true_task = _time_restart_true_task if _time_restart_true_task is not None else 3600


# включение логирование запросов в БД
_log_state_db = get_log_state_db()
log_state_db = _log_state_db if _log_state_db is not None else 0

# имя БД
_db_name = get_db_name()
db_name = _db_name if _db_name is not None else 'sqlite_python_alchemy.db'
