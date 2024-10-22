import os
from datetime import datetime

from sqlalchemy import and_, func, insert, select, update

from config import db_name
from db_handler_init import (
    init_get_meter,
    init_get_meter_msg,
    init_get_meter_wl,
    init_get_task_equipment,
    init_get_task_equipment_for_handler,
    init_get_uspd,
)
from sql.engine import get_async_session
from sql.model import (
    EquipmentHandModelUpdate,
    EquipmentModelGet,
    EquipmentModelSet,
    LogHandModelSet,
    MeterModelGet,
    MeterModelSet,
    MeterModelUpdate,
    MeterMsgHandModelGet,
    MeterWLHandModelGet,
    MsgModelSet,
    TaskEquipmentHandlerModelGet,
    TaskEquipmentModelGet,
    TaskHandModelUpdate,
    TaskModelSet,
    TaskModelUpdate,
    WLModelSet,
    WLModelUpdate,
)
from sql.scheme import Equipment, GroupTask, LogEquipment, Messages, Meter, Task, Wl, create_db


async def start_db(type_start):
    if type_start == 'clear':
        try:
            os.remove(db_name)
        except FileNotFoundError as ex:
            print(ex.args)

    await create_db()


async def get_equipment_filter(in_equipments: list[str]) -> list[EquipmentModelGet]:
    """получение всех УСПД из БД по номерам из файла host.xlsx"""
    stmt = select(Equipment).where(Equipment.serial_in_sourse.in_(in_equipments))

    session = [session async for session in get_async_session()][0]

    result = await session.execute(stmt)

    uspd_get = []

    for a in result.scalars():
        uspd_get.append(init_get_uspd(a))

    await session.close()

    return uspd_get


async def set_equipment(equipment: list[EquipmentModelSet]) -> None:
    # a = [line_eq.model_dump(exclude_none=True) for line_eq in equipment]
    stmt = insert(Equipment).values([line_eq.model_dump() for line_eq in equipment])

    session = [session async for session in get_async_session()][0]

    await session.execute(stmt)
    await session.commit()
    await session.close()


async def get_task_equipment_filter(equipment_id: list[int]) -> list[TaskEquipmentModelGet]:
    """получение всех task из БД по equipment_id"""
    stmt = select(Task, Equipment).join(Task.equipment).where(Task.equipment_id.in_(equipment_id))
    # stmt = select(Task).where(Task.equipment_id.in_(equipment_id))

    session = [session async for session in get_async_session()][0]

    result = await session.execute(stmt)

    uspd_get = []

    for line in result.scalars():
        uspd_get.append(init_get_task_equipment(line))

    await session.close()

    return uspd_get


async def set_task(task: list[TaskModelSet]) -> None:
    session = [session async for session in get_async_session()][0]
    try:
        stmt = insert(Task).values([line_t.model_dump(exclude_none=True) for line_t in task])

        await session.execute(stmt)
        await session.commit()
        await session.close()
    except Exception as ex:
        print(ex.args)


async def get_task_grouptask(group_task_id: int, time_zone: int) -> list[TaskEquipmentHandlerModelGet]:
    """получение всех task из БД по equipment_id"""
    stmt = select(Task, Equipment).join(Task.equipment).where(Task.group_task_id.in_([group_task_id]))

    session = [session async for session in get_async_session()][0]

    result = await session.execute(stmt)

    task_get = []

    for line in result.scalars():
        task_get.append(await init_get_task_equipment_for_handler(line, time_zone))
    await session.close()

    return task_get


async def update_task(task: list[TaskModelUpdate]) -> None:
    data_update = [line_t.model_dump(exclude_none=True) for line_t in task]

    session = [session async for session in get_async_session()][0]

    stmt = update(Task)
    # print(stmt)
    await session.execute(stmt, data_update)
    await session.commit()
    await session.close()


async def set_grouptask() -> int:
    stmt = insert(GroupTask).returning(GroupTask.group_task_id)

    session = [session async for session in get_async_session()][0]

    result = await session.execute(stmt)
    await session.commit()

    group_task_id = None
    for line in result.scalars():
        group_task_id = line
        break

    await session.close()

    return group_task_id


async def get_meter_filter(in_meter: list[str]) -> list[MeterModelGet]:
    """получение всех ПУ из БД по номеру"""
    stmt = select(Meter).where(Meter.modem.in_(in_meter))

    session = [session async for session in get_async_session()][0]

    result = await session.execute(stmt)

    uspd_get = []

    for a in result.scalars():
        uspd_get.append(init_get_meter(a))

    await session.close()

    return uspd_get


async def get_meter_wl_filter(in_meter: list[str], equipment_id) -> list[MeterWLHandModelGet]:
    """получение всех ПУ из БД по номеру"""
    stmt = (
        select(Meter, Wl)
        .join(Meter.wl)
        .where(
            and_(
                Meter.modem.in_(in_meter),
                Wl.equipment_id == equipment_id,
            ),
        )
    )

    session = [session async for session in get_async_session()][0]

    result = await session.execute(stmt)

    uspd_get = []

    for a in result.scalars():
        uspd_get.append(init_get_meter_wl(a))

    await session.close()

    return uspd_get


async def get_max_time_saved_filter_equipment(equipment_id) -> datetime:
    """Получение максимальной даты сохрарения пакетов в УСПД по конкретной УСПД"""
    stmt = select(func.max(Messages.time_saved)).where(Messages.equipment_id == equipment_id)

    session = [session async for session in get_async_session()][0]

    result = await session.execute(stmt)

    max_time_saved = None

    for a in result.scalars():
        max_time_saved = a

    await session.close()

    return max_time_saved


async def set_meter(meter: list[MeterModelSet]) -> None:
    # a = [line_eq.model_dump(exclude_none=True) for line_eq in equipment]

    session = [session async for session in get_async_session()][0]
    try:
        stmt = insert(Meter).values([line_m.model_dump() for line_m in meter])
        await session.execute(stmt)
        await session.commit()
        result = None
    except Exception as ex:
        await session.rollback()
        result = ex.args
        print(f'{datetime.now()}: ---------- Ошибка записи в БД сервиса: {ex.args}, set_meter')
    await session.close()
    return result


async def update_meter(meter: list[MeterModelUpdate]) -> None:
    session = [session async for session in get_async_session()][0]
    try:
        data_update = [line_m.model_dump() for line_m in meter]
        stmt = update(Meter)
        # print(stmt)
        await session.execute(stmt, data_update)
        await session.commit()
        result = None
    except Exception as ex:
        await session.rollback()
        result = ex.args
        print(f'{datetime.now()}: ---------- Ошибка записи в БД сервиса: {ex.args}, update_meter')
    await session.close()
    return result


async def get_meter_msg_filter(in_meter: list[str], equipment_id) -> list[MeterMsgHandModelGet]:
    """получение всех ПУ из БД по номеру"""
    stmt = (
        select(Meter, Messages)
        .join(Meter.messages)
        .where(
            and_(
                Meter.modem.in_(in_meter),
                Wl.equipment_id == equipment_id,
            ),
        )
    )

    session = [session async for session in get_async_session()][0]

    result = await session.execute(stmt)

    uspd_get = []

    for a in result.scalars():
        uspd_get.append(init_get_meter_msg(a))

    await session.close()

    return uspd_get


async def update_data_after_hand(
    task: TaskHandModelUpdate,
    equipment: EquipmentHandModelUpdate | None,
    meter_wl: dict[list[WLModelSet], list[WLModelUpdate]],
    meter_msg: list[MsgModelSet],
    log: LogHandModelSet,
) -> None:
    """Занесение результатов по одной таске get_command"""
    session = [session async for session in get_async_session()][0]
    try:
        task_update = [task.model_dump()]
        stmt_task = update(Task)
        await session.execute(stmt_task, task_update)

        if equipment is not None:
            equipment_update = [equipment.model_dump()]
            stmt_equipment = update(Equipment)
            await session.execute(stmt_equipment, equipment_update)

        if meter_wl is not None:
            if len(meter_wl['update_wl']) > 0:
                update_wl_update = [line_umwl.model_dump(exclude_none=True) for line_umwl in meter_wl['update_wl']]
                stmt_meter_wl_update = update(Wl)
                await session.execute(stmt_meter_wl_update, update_wl_update)

            if len(meter_wl['create_wl']) > 0:
                update_wl_create = [line_cmwl.model_dump() for line_cmwl in meter_wl['create_wl']]
                meter_wl_create = insert(Wl).values(update_wl_create)
                await session.execute(meter_wl_create)

        if meter_msg is not None and len(meter_msg) > 0:
            msg_create = [line_msg.model_dump() for line_msg in meter_msg]
            meter_msg_create = insert(Messages).values(msg_create)
            await session.execute(meter_msg_create)

        stmt_log = insert(LogEquipment).values([log.model_dump()])
        await session.execute(stmt_log)

        await session.commit()
    except Exception as ex:
        await session.rollback()
        print(f'{datetime.now()}: ---------- Ошибка записи в БД сервиса: {ex.args}, task: {task.task_id}')
    await session.close()
