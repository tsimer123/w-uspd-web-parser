from datetime import datetime

from config import list_msg_command
from handlers.handler_get_command import hand_result
from logics.get_messages import get_messages
from logics.get_wl import get_wl
from sql.model import TaskEquipmentHandlerModelGet


async def run_command(task_rb: TaskEquipmentHandlerModelGet):
    result = {'status': False}
    print(
        f'{datetime.now()}: start run_command for task {task_rb.task_id}, equipment {task_rb.serial_in_sourse}, command: {task_rb.type_task}'
    )

    if task_rb.type_task == 'get_wl':
        result = await get_wl(task_rb)
        await hand_result(result)

    if task_rb.type_task in list_msg_command:
        result = await get_messages(task_rb)
        await hand_result(result)

    print(
        f'{datetime.now()}: stop run_command for task {task_rb.task_id}, equipment {task_rb.serial_in_sourse}, command: {task_rb.type_task}'
    )


# get_messages
