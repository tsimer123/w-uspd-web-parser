import asyncio
from asyncio import Queue
from datetime import datetime, timedelta

# from handler_commands import run_command
from config import list_command, time_restart_true_task, timeout_task
from data_class.data_equipment import EquipmentInExcel, UspdEquipmentInExcel
from db_handler import (
    get_equipment_filter,
    get_task_equipment_filter,
    get_task_grouptask,
    set_equipment,
    set_grouptask,
    set_task,
    update_task,
)
from excel import open_excel
from funcs.decorators import repit_access_to_db_not_out
from handler_commands import run_command
from sql.model import (
    EquipmentModelGet,
    EquipmentModelSet,
    TaskEquipmentHandlerModelGet,
    TaskEquipmentModelGet,
    TaskModelGet,
    TaskModelSet,
    TaskModelUpdate,
)


def clear_sourse_uspd(uspd: list[list]) -> list[list]:
    # print(f'{datetime.now()}: start clear_sourse_uspd')
    count_u = 0

    while count_u < len(uspd):
        if len(uspd[count_u]) > 2 and uspd[count_u][2] is None:
            uspd[count_u][2] = None
        count_u += 1
    # print(f'{datetime.now()}: stop clear_sourse_uspd')
    return uspd


def valid_сcommand_param(uspd: list[list]) -> None:
    # print(f'{datetime.now()}: start command_valid_param')
    # set_shedule_param = set(list_shedule_param)
    for line in uspd:
        # проверка правильность записи команды
        if line[4] in list_command:
            pass
            # проверка параметров для команды set_shedule
            # if line[4] == 'set_shedule':
            #     paramData = str(line[5]).split(',')
            #     if len(paramData) == 4:
            #         paramDataSet: set = set(paramData)
            #         if paramDataSet.issubset(set_shedule_param) is False:
            #             raise Exception(f'Не правильные параметры комады set_shedule для УСПД {line[0]}')
            #     else:
            #         raise Exception(
            #             f'Количество параметров для комады set_shedule для УСПД {line[0]} не раврно 4 {paramData}'
            #         )
        else:
            raise Exception(f'Неизвестная команда {line[4]}')

    # print(f'{datetime.now()}: stop convert_sours_to_dict')


def convert_sours_to_dict(uspd: list[list]) -> list[EquipmentInExcel]:
    # print(f'{datetime.now()}: start convert_sours_to_dict')
    result = []
    count = 1
    for line in uspd:
        temp_uspd = UspdEquipmentInExcel(name=str(line[0]), ip1=line[1], ip2=line[2])
        if len(line) < 6:
            param_data = None
        else:
            param_data = None if line[5] is None else str(line[5])
        # param_data = None if len(line) < 6 else str(line[5])
        temp_dict = EquipmentInExcel(uspd=temp_uspd, command=line[4], param_data=param_data)
        result.append(temp_dict)
        count += 1
    # print(f'{datetime.now()}: stop convert_sours_to_dict')
    return result


def get_number_equipment(uspd: list[EquipmentInExcel]) -> list[str]:
    equipment_in = []
    for line_u in uspd:
        trigger_e = 0
        for line_e in equipment_in:
            if line_u.uspd.name == line_e:
                trigger_e = 1
                break
        if trigger_e == 0:
            equipment_in.append(line_u.uspd.name)
    return equipment_in


def get_equipment_not_in_db(
    uspd_in: list[EquipmentInExcel], uspd_db: list[EquipmentModelGet]
) -> list[EquipmentInExcel]:
    """функция ищет УСПД, которых нет в БД"""
    uspd_not_in_db = []
    for line_in in uspd_in:
        trigger_uspd = 0
        for line_db in uspd_db:
            if line_in.uspd.name == line_db.serial_in_sourse:
                trigger_uspd = 1
                break
        if trigger_uspd == 0:
            uspd_not_in_db.append(line_in)
    return uspd_not_in_db


def init_set_uspd(equipment: list[EquipmentInExcel]) -> list[EquipmentModelSet]:
    result: list[EquipmentModelSet] = []

    for line in equipment:
        trigger_e = 0
        for line_r in result:
            if line_r.serial_in_sourse == line.uspd.name:
                trigger_e = 1
                break
        if trigger_e == 0:
            result.append(
                EquipmentModelSet(
                    serial_in_sourse=line.uspd.name,
                    ip1=str(line.uspd.ip1),
                    ip2=str(line.uspd.ip2) if line.uspd.ip2 is not None else None,
                )
            )

    return result


def init_set_task_start(
    equipment: list[EquipmentModelGet], uspd_in: list[EquipmentInExcel], group_task_id
) -> list[TaskModelSet]:
    result = []

    for line_u in uspd_in:
        for line_e in equipment:
            if line_e.serial_in_sourse == line_u.uspd.name:
                result.append(
                    TaskModelSet(
                        equipment_id=line_e.equipment_id,
                        type_task=line_u.command,
                        status_task='start',
                        timeouut_task=timeout_task[line_u.command],
                        group_task_id=group_task_id,
                        # param_data=line_u.param_data,
                    )
                )
                break

    return result


def get_continue_task(
    group_task_id: int,
    task: list[TaskEquipmentModelGet],
    uspd_in: list[EquipmentInExcel],
    equipment: list[EquipmentModelGet],
) -> dict[list[TaskModelUpdate], list[EquipmentInExcel]]:
    result = {
        'change_task': [],
        'eq_not_task': [],
    }

    for line_uin in uspd_in:
        trigger_e = 0
        for line_t in task:
            if line_uin.uspd.name == line_t.serial_in_sourse and line_uin.command == line_t.type_task:
                if line_t.status_task == 'start':
                    timeout_for_task = line_t.update_on + timedelta(seconds=line_t.timeouut_task)
                    if timeout_for_task < datetime.now():
                        result['change_task'].append(
                            TaskModelUpdate(
                                task_id=line_t.task_id,
                                group_task_id=group_task_id,
                                timeouut_task=line_t.timeouut_task,
                            )
                        )
                    trigger_e = 1
                    break
                if line_t.status_task == 'false':
                    result['change_task'].append(
                        TaskModelUpdate(
                            task_id=line_t.task_id,
                            group_task_id=group_task_id,
                            status_task='start',
                            timeouut_task=line_t.timeouut_task,
                        )
                    )
                    trigger_e = 1
                    break
                # time_restart_true_task
                timeout_restart_true = line_t.update_on + timedelta(seconds=time_restart_true_task)
                if line_t.status_task == 'true':
                    if timeout_restart_true < datetime.now():
                        result['change_task'].append(
                            TaskModelUpdate(
                                task_id=line_t.task_id,
                                group_task_id=group_task_id,
                                status_task='start',
                                timeouut_task=line_t.timeouut_task,
                            )
                        )
                    trigger_e = 1
                    break
        if trigger_e == 0:
            for line_e in equipment:
                if line_uin.uspd.name == line_e.serial_in_sourse:
                    result['eq_not_task'].append(line_uin)
    return result


def get_restart_task(
    task: list[TaskEquipmentModelGet],
    uspd_in: list[EquipmentInExcel],
    equipment: list[EquipmentModelGet],
) -> dict[list[TaskModelGet], list[EquipmentModelGet]]:
    result = {
        'change_task': [],
        'eq_not_task': [],
    }

    for line_uin in uspd_in:
        trigger_e = 0
        for line_t in task:
            if line_uin.uspd.name == line_t.serial_in_sourse and line_uin.command == line_t.type_task:
                line_t.meter_true = None
                result['change_task'].append(line_t)
                trigger_e = 1
                break
        if trigger_e == 0:
            for line_e in equipment:
                if line_uin.uspd.name == line_e.serial_in_sourse:
                    result['eq_not_task'].append(line_e)
    return task


@repit_access_to_db_not_out
async def update_task_write_db(data):
    await update_task(data)


async def get_task(
    type_start: str, counter_iter: int, group_task_id: int, time_zone: int
) -> list[TaskEquipmentHandlerModelGet]:
    # print(f'{datetime.now()}: start get_task_from_excel')
    # получаем из excel файла задания  (УСПД с командой)
    data = open_excel('host.xlsx')
    # убираем None если нет второго ip
    # data = clear_sourse_uspd(excel_data)
    # првоерям правильность записи команд в excel
    valid_сcommand_param(data)
    # преобразовываем список в список классов pydantic (удобно сериализовать в sqlalchemy)
    data = convert_sours_to_dict(data)
    # получаем списосок имен УСПД из Excel
    equipment_name = get_number_equipment(data)
    if counter_iter == 0:
        # если первая итерация по файлу host.xlsx, то готовим БД
        if type_start != 'clear':
            # получаем список УСПД из БД
            uspd_in_db = await get_equipment_filter(equipment_name)
            # получаем список УСПД, которых нет в БД
            uspd_not_in_db = get_equipment_not_in_db(data, uspd_in_db)
            if len(uspd_not_in_db) > 0:
                await set_equipment(init_set_uspd(uspd_not_in_db))
        else:
            # создать все УСПД в БД
            await set_equipment(init_set_uspd(data))
    # получаем все УСПД из БД, после добавления недостающих
    uspd_in_db = await get_equipment_filter(equipment_name)

    if type_start == 'clear' and counter_iter == 0:
        # если запуск с параметром clear то создаем стартовые таски
        task_start = init_set_task_start(uspd_in_db, data, group_task_id)
        await set_task(task_start)
    else:
        equipment_id = [equipment.equipment_id for equipment in uspd_in_db]
        # получаем все таски по id УСПД
        task_equipment = await get_task_equipment_filter(equipment_id)
        if type_start == 'continue' or (type_start == 'clear' and counter_iter != 0):
            # если запуск с параметром continue то пересоздаем просроченные стартовые или неудачные таски
            # или отклыдываем их
            contunue_task = get_continue_task(group_task_id, task_equipment, data, uspd_in_db)
            if len(contunue_task['change_task']) > 0:
                await update_task_write_db(contunue_task['change_task'])
            if len(contunue_task['eq_not_task']) > 0:
                task_contimue_new_eqp = init_set_task_start(uspd_in_db, contunue_task['eq_not_task'], group_task_id)
                await set_task(task_contimue_new_eqp)
        if type_start == 'restart':
            # если запуск с параметром restart то пересоздаем все таски
            restart_task = get_restart_task(task_equipment, uspd_in_db)
            if len(restart_task['change_task']) > 0:
                await update_task_write_db(restart_task['change_task'])
            if len(restart_task['eq_not_task']) > 0:
                new_task = init_set_task_start(restart_task['eq_not_task'], data)
                await set_task(new_task)
    task_for_handler = await get_task_grouptask(group_task_id, time_zone)
    return task_for_handler


async def get_ip_from_excel(queue: Queue):
    while True:
        task = await queue.get()
        # start_time = datetime.now()
        await run_command(task)
        # end_time = datetime.now()
        # delta = end_time - start_time
        # delta = delta.total_seconds()
        queue.task_done()


async def customer_generator_from_excel(queue: Queue, interval_t: float, type_start: str, time_zone: int):
    print(f'{datetime.now()}: start loop customer_generator_from_excel')
    counter_iter = 0
    group_task_id = await set_grouptask()
    while True:
        print(f'{datetime.now()}: start iter customer_generator_from_excel')
        # получаем из Excel список словарей -  заданий (УСПД с командой)

        task = await get_task(type_start, counter_iter, group_task_id, time_zone)
        len_task = len(task)
        print(f'{datetime.now()}: из Excel получено заданий: {len_task}')

        # print(f'{datetime.now()}: размер очереди: {queue.qsize()}')
        # print(f'{datetime.now()}: проверка на пустое: {queue.empty()}')

        if len(task) > 0:
            count_uqipment_q = 0
            for line in task:
                await queue.put(line)
                # print('Добавили УСПД в очередь!')
                count_uqipment_q += 1
            print(f'{datetime.now()}: Добавили {count_uqipment_q} УСПД в очередь')
        else:
            print(f'{datetime.now()}: Нет заданий для отработки')
        # print(f'{datetime.now()}: размер очереди: {queue.qsize()}')
        # print(f'{datetime.now()}: проверка на пустое: {queue.empty()}')
        print(f'{datetime.now()}: stop iter customer_generator_from_excel')
        await asyncio.sleep(interval_t)
        counter_iter += 1
        # print(f'{datetime.now()}: stop loop customer_generator_from_excel')
