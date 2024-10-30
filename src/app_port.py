import asyncio
import datetime
from asyncio import Queue

from argument_start import get_args
from creat_task_port import customer_generator_from_excel, get_ip_from_excel
from db_handler import start_db


async def main():
    print(f'{datetime.datetime.now()}: Запуск приложения')

    args = get_args()

    type_start = args['type']
    interval = args['interval']
    queue_count = args['queue_count']
    handler_count = args['handler_count']
    time_zone = args['time_zone']

    print(
        f'{datetime.datetime.now()}: параметры запуска: \ntype={type_start} \ninterval={interval} \nqueue_count={queue_count} \nhandler_count={handler_count}'
    )

    await start_db(type_start)

    # print(1)

    customer_queue = Queue(queue_count)

    customer_producer = asyncio.create_task(
        customer_generator_from_excel(customer_queue, interval, type_start, time_zone)
    )

    cashiers = [asyncio.create_task(get_ip_from_excel(customer_queue)) for i in range(handler_count)]

    await asyncio.gather(customer_producer, *cashiers)


asyncio.run(main())

# параметры запуска:
# - t=['continue', 'restart', 'clear']- тип запуска
# - i=100 - интервал перезапуска
# - q=100 - размер очереди
# - h=100 - количество обработчиков
