user_agent = (
    'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
)

# имя БД
db_name = 'sqlite_python_alchemy.db'

# время ожидания статуса wait для get_shedule в секундах
timeout_task = {
    'get_wl': 1800,
    'get_messages': 1800,
}

# перечень команд для функции get_command
list_command = [
    'get_wl',
    'get_messages',
]

# время перезапуска true тасок
time_restart_true_task = 43200  #  11:59:59
