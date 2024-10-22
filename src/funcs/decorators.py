from asyncio import sleep
from functools import wraps
from random import randint


def repit_access_to_db_not_out(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        for _ in range(1, 10, 1):
            resutl_set_meter = await func(*args, **kwargs)
            if resutl_set_meter is not None:
                sleep(randint(1, 5))
                print(f'---------Ошибка при записи в БД: {resutl_set_meter} из функции : {func.__name__}, спим недолго')
                resutl_set_meter = await func(*args, **kwargs)
                if resutl_set_meter is None:
                    break
            else:
                break

    return wrapper
