from asyncio import sleep
from functools import wraps
from random import randint


def repit_access_to_db_not_out(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        while True:
            # if isinstance(args[0], TaskHandModelUpdate):
            #     print(args[0].task_id)
            resutl_set_meter = await func(*args, **kwargs)
            if resutl_set_meter is not None:
                await sleep(randint(1, 10))
                print(f'---------Ошибка при записи в БД: {resutl_set_meter} из функции : {func.__name__}, спим недолго')
            else:
                break
        return resutl_set_meter

    return wrapper


def repit_access_to_db_present_out(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        while True:
            # a = func.__name__
            resutl_set_meter = await func(*args, **kwargs)
            if resutl_set_meter is not None and 'error' in resutl_set_meter and 'UNIQUE' not in resutl_set_meter[0]:
                await sleep(randint(1, 10))
                print(f'---------Ошибка при записи в БД: {resutl_set_meter} из функции : {func.__name__}, спим недолго')
            else:
                break
        return resutl_set_meter

    return wrapper
