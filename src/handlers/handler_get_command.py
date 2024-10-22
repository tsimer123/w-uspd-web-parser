from datetime import datetime

from config import timeout_task
from data_class.data_get_command import GetComandModel, MeterPacketModel, MeterWlModel
from db_handler import (
    get_max_time_saved_filter_equipment,
    get_meter_filter,
    get_meter_wl_filter,
    set_meter,
    update_data_after_hand,
    update_meter,
)
from funcs.decorators import repit_access_to_db_not_out
from sql.model import (
    EquipmentHandModelUpdate,
    LogHandModelSet,
    MeterModelGet,
    MeterModelSet,
    MeterModelUpdate,
    MeterWLHandModelGet,
    MsgModelSet,
    TaskHandModelUpdate,
    WLModelSet,
    WLModelUpdate,
)


@repit_access_to_db_not_out
async def set_result_handler(task, equipment, meter_wl, meter_msg, log):
    await update_data_after_hand(task, equipment, meter_wl, meter_msg, log)


async def hand_result(result_in: GetComandModel):
    start_time = datetime.now()
    print(f'{datetime.now()}: start write data for task {result_in.task_id}')
    # при обновлении таски брать все даже None
    task = hand_task(result_in)
    equipment = hand_equipment(result_in)
    if result_in.type_task == 'get_wl':
        meter_wl = await hand_wl(result_in)
    else:
        meter_wl = None

    if result_in.type_task == 'get_messages':
        meter_msg = await hand_messages(result_in)
    else:
        meter_msg = None

    log = hand_log(result_in)

    await set_result_handler(task, equipment, meter_wl, meter_msg, log)

    end_time = datetime.now()
    delta = end_time - start_time
    total_time = round(delta.total_seconds())

    print(f'{datetime.now()}: stop write data for task {result_in.task_id}, , total time {total_time}')


def get_list_meter(meters: list[MeterWlModel] | list[MeterPacketModel]) -> list[int]:
    result = []
    for line in meters:
        result.append(line.number)
    return result


def hand_task(result_in: GetComandModel) -> TaskHandModelUpdate:
    result = TaskHandModelUpdate(
        task_id=result_in.task_id,
        status_task=result_in.status_task,
        total_time=result_in.total_time,
        timeouut_task=timeout_task[result_in.type_task],
        error=result_in.error,
    )

    return result


def hand_equipment(result_in: GetComandModel) -> EquipmentHandModelUpdate | None:
    if result_in.equipment_info is not None and result_in.equipment_info.status is True:
        result = EquipmentHandModelUpdate(
            equipment_id=result_in.equipment_id,
            serial=result_in.equipment_info.serial,
            bs_type=result_in.equipment_info.bs_type,
            mode=result_in.equipment_info.mode,
            dl_aver_busyness=result_in.equipment_info.dl_aver_busyness,
            rev_list=result_in.equipment_info.rev_list,
            latitude=result_in.equipment_info.latitude,
            longitude=result_in.equipment_info.longitude,
        )
        return result
    else:
        return None


# def repit_access_to_db_not_out(func):
#     async def wrapper(*args, **kwargs):
#         for _ in range(1, 10, 1):
#             resutl_set_meter = await func(*args, **kwargs)
#             if resutl_set_meter is not None:
#                 sleep(randint(1, 5))
#                 print(f'---------Ошибка при записи в БД {resutl_set_meter}, спим')
#                 resutl_set_meter = await func(*args, **kwargs)
#                 if resutl_set_meter is None:
#                     break
#             else:
#                 break

#     return wrapper


@repit_access_to_db_not_out
async def set_meter_write_db(data_list):
    await set_meter(data_list)


async def update_meter_write_db(data_list):
    await update_meter(data_list)


async def hand_wl(result_in: GetComandModel) -> dict[list[WLModelSet], list[WLModelUpdate]]:
    dict_result = {
        'create_wl': [],
        'update_wl': [],
    }
    if (
        result_in.meter_wl is not None
        and result_in.meter_wl.status is True
        and result_in.meter_wl.meter_wl is not None
        and len(result_in.meter_wl.meter_wl) > 0
    ):
        list_meter = get_list_meter(result_in.meter_wl.meter_wl)
        meter_from_db = await get_meter_filter(list_meter)
        meter_wl_from_db = await get_meter_wl_filter(list_meter, result_in.equipment_id)

        # ищем ПУ из ВЛ УСПД в БД, если их в БД нет то создаем новые
        meter = get_create_meter_wl(result_in, meter_from_db)
        if len(meter['create_meter']) > 0:
            await set_meter_write_db(meter['create_meter'])
        if len(meter['update_meter']) > 0:
            await update_meter_write_db(meter['update_meter'])

        meter_from_db = await get_meter_filter(list_meter)
        # готовим данные для создания новых ВЛ в БД
        dict_result['create_wl'] = get_create_wl(meter_wl_from_db, result_in, meter_from_db)

        # готовим данные для обновления ВЛ в БД
        dict_result['update_wl'] = get_update_wl(meter_wl_from_db, result_in)

    return dict_result


def get_create_meter_wl(
    result_in: GetComandModel, meter_from_db: list[MeterModelGet]
) -> dict[list[MeterModelSet], list[MeterModelUpdate]]:
    result = {
        'create_meter': [],
        'update_meter': [],
    }

    for line_mwl in result_in.meter_wl.meter_wl:
        trigger_meter_create = 0
        for line_mfd in meter_from_db:
            if line_mwl.number == line_mfd.modem:
                trigger_meter_create = 1
                if line_mfd.hw_type is None:
                    result['update_meter'].append(
                        MeterModelUpdate(meter_id=line_mfd.meter_id, hw_type=line_mwl.hw_type)
                    )
                break
        if trigger_meter_create == 0:
            result['create_meter'].append(MeterModelSet(modem=line_mwl.number, hw_type=line_mwl.hw_type))
    return result


def get_create_wl(
    meter_wl_from_db: list[MeterWLHandModelGet], result_in: GetComandModel, meter_from_db: list[MeterModelGet]
) -> list[WLModelSet]:
    meter_in_wl = [line_tmwl.modem for line_tmwl in meter_wl_from_db]
    create_wl = []
    for line_db in meter_from_db:
        if line_db.modem not in meter_in_wl:
            for line_mwl in result_in.meter_wl.meter_wl:
                if line_db.modem == line_mwl.number:
                    create_wl.append(
                        WLModelSet(
                            equipment_id=result_in.equipment_id,
                            meter_id=line_db.meter_id,
                            last_success=line_mwl.last_success_dl_ts,
                            present=True,
                        )
                    )
    return create_wl


def get_update_wl(meter_wl_from_db: list[MeterWLHandModelGet], result_in: GetComandModel) -> list[WLModelUpdate]:
    update_wl = []
    for line_dwl in meter_wl_from_db:
        trigger_upd = 0
        for line_mwl in result_in.meter_wl.meter_wl:
            if line_dwl.modem == line_mwl.number:
                update_wl.append(
                    WLModelUpdate(
                        wl_id=line_dwl.wl_id,
                        last_success=line_mwl.last_success_dl_ts,
                        present=True,
                    )
                )
                trigger_upd = 1
                break
        if trigger_upd == 0:
            update_wl.append(WLModelUpdate(wl_id=line_dwl.wl_id, present=False))

    return update_wl


async def hand_messages(result_in: GetComandModel) -> list[MsgModelSet]:
    create_wl = []
    if (
        result_in.meter_packet is not None
        and result_in.meter_packet.status is True
        and result_in.meter_packet.meter_packet is not None
        and len(result_in.meter_packet.meter_packet) > 0
    ):
        list_meter = get_list_meter(result_in.meter_packet.meter_packet)
        meter_from_db = await get_meter_filter(list_meter)
        # meter_wl_from_db = await get_meter_msg_filter(list_meter, result_in.equipment_id)

        # ищем ПУ из ВЛ УСПД в БД, если их в БД нет то создаем новые
        create_meter = get_create_meter_msg(result_in, meter_from_db)
        if len(create_meter) > 0:
            await set_meter_write_db(create_meter)

        meter_from_db = await get_meter_filter(list_meter)
        # готовим данные для создания новых ВЛ в БД
        max_time_saved = await get_max_time_saved_filter_equipment(result_in.equipment_id)

        create_wl = get_create_msg(result_in, meter_from_db, max_time_saved)

    return create_wl


def get_create_meter_msg(
    result_in: GetComandModel, meter_from_db: list[MeterModelGet]
) -> dict[list[MeterModelSet], list[MeterModelUpdate]]:
    result = []

    meters_uspd = set([line_mwl.number for line_mwl in result_in.meter_packet.meter_packet])
    meters_db = set([line_mfd.modem for line_mfd in meter_from_db])

    meters_for_db = meters_uspd - meters_db

    for line_mfdb in meters_for_db:
        result.append(MeterModelSet(modem=line_mfdb))

    # for line_mwl in result_in.meter_packet.meter_packet:
    #     trigger_meter_create = 0
    #     for line_mfd in meter_from_db:
    #         if line_mwl.number == line_mfd.modem:
    #             trigger_meter_create = 1
    #             break
    #     if trigger_meter_create == 0:
    #         result.append(MeterModelSet(modem=line_mwl.number))
    return result


def get_create_msg(
    result_in: GetComandModel, meter_from_db: list[MeterModelGet], max_time_saved: datetime | None
) -> list[MsgModelSet]:
    # добавить првоерку на старые пакеты
    if max_time_saved is None:
        max_time_saved = datetime(1990, 2, 20)
    create_msg = []
    for line_mwl in result_in.meter_packet.meter_packet:
        # print(datetime.fromtimestamp(line_mwl.time_saved))
        if datetime.fromtimestamp(line_mwl.time_saved) > max_time_saved:
            for line_db in meter_from_db:
                if line_db.modem == line_mwl.number:
                    create_msg.append(
                        MsgModelSet(
                            equipment_id=result_in.equipment_id,
                            meter_id=line_db.meter_id,
                            type_packet=line_mwl.type_packet,
                            time_detected=datetime.fromtimestamp(line_mwl.time_detected),
                            time_saved=datetime.fromtimestamp(line_mwl.time_saved),
                        )
                    )
                    break
    return create_msg


def hand_log(result_in: GetComandModel) -> LogHandModelSet:
    list_response = None

    if result_in is not None:
        list_response = str(result_in.model_dump(exclude_unset=True))

    status_response = bool(len(list_response))

    result = LogHandModelSet(
        task_id=result_in.task_id,
        equipment_id=result_in.equipment_id,
        status_response=status_response,
        response=list_response,
    )

    return result
