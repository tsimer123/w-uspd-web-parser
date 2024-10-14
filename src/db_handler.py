import os

from sqlalchemy import and_, insert, select, update

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
from sql.scheme import Equipment, GroupTask, Messages, Meter, Task, Wl, create_db


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


async def set_meter(meter: list[MeterModelSet]) -> None:
    # a = [line_eq.model_dump(exclude_none=True) for line_eq in equipment]
    stmt = insert(Meter).values([line_m.model_dump() for line_m in meter])

    session = [session async for session in get_async_session()][0]

    await session.execute(stmt)
    await session.commit()
    await session.close()


async def update_meter(meter: list[MeterModelUpdate]) -> None:
    data_update = [line_m.model_dump() for line_m in meter]

    session = [session async for session in get_async_session()][0]

    stmt = update(Meter)
    # print(stmt)
    await session.execute(stmt, data_update)
    await session.commit()
    await session.close()


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

        if len(meter['update_meter']) > 0:
            meter_update = [line_um.model_dump(exclude_none=True) for line_um in meter['update_meter']]
            stmt_meter_update = update(Meter)
            await session.execute(stmt_meter_update, meter_update)

        if len(meter['create_meter']) > 0:
            value = [line_cm.model_dump() for line_cm in meter['create_meter']]
            meter_create = insert(Meter).values(value)
            # print('111111111111')
            # print(meter_create)
            await session.execute(meter_create)

        stmt_log = insert(LogEquipment).values([log.model_dump()])
        await session.execute(stmt_log)

        await session.commit()
    except Exception as ex:
        await session.rollback()
        print(f'{datetime.now()}: ---------- Ошибка записи в БД сервиса: {ex.args}')
    await session.close()
