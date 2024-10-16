from datetime import datetime

from config import timeout_task
from data_class.data_get_command import GetComandModel, MeterWlModel
from db_handler import (
    get_meter_filter,
    get_meter_wl_filter,
    set_meter,
    update_data_after_hand,
    update_meter,
)
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


# 'get_wl',
#     'get_messages',
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

    await update_data_after_hand(task, equipment, meter_wl, meter_msg, log)

    end_time = datetime.now()
    delta = end_time - start_time
    total_time = round(delta.total_seconds())

    print(f'{datetime.now()}: stop write data for task {result_in.task_id}, , total time {total_time}')


def get_list_meter(meter_wl: list[MeterWlModel]) -> list[int]:
    result = []
    for line in meter_wl:
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
            await set_meter(meter['create_meter'])
        if len(meter['update_meter']) > 0:
            await update_meter(meter['update_meter'])

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
                    result['create_meter'].append(
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
        list_meter = get_list_meter(result_in.meter_wl.meter_wl)
        meter_from_db = await get_meter_filter(list_meter)
        # meter_wl_from_db = await get_meter_msg_filter(list_meter, result_in.equipment_id)

        # ищем ПУ из ВЛ УСПД в БД, если их в БД нет то создаем новые
        create_meter = get_create_meter_msg(result_in, meter_from_db)
        await set_meter(create_meter)

        meter_from_db = await get_meter_filter(list_meter)
        # готовим данные для создания новых ВЛ в БД
        create_wl = get_create_msg(result_in, meter_from_db)

    return create_wl


def get_create_meter_msg(
    result_in: GetComandModel, meter_from_db: list[MeterModelGet]
) -> dict[list[MeterModelSet], list[MeterModelUpdate]]:
    result = []

    for line_mwl in result_in.meter_wl.meter_wl:
        trigger_meter_create = 0
        for line_mfd in meter_from_db:
            if line_mwl.number == line_mfd.modem:
                trigger_meter_create = 1
                break
        if trigger_meter_create == 0:
            result.append(MeterModelSet(modem=line_mwl.number))
    return result


def get_create_msg(result_in: GetComandModel, meter_from_db: list[MeterModelGet]) -> list[MsgModelSet]:
    create_msg = []
    for line_mwl in result_in.meter_packet.meter_packet:
        for line_db in meter_from_db:
            if line_db.modem == line_mwl.meter_number:
                create_msg.append(
                    MsgModelSet(
                        equipment_id=result_in.equipment_id,
                        meter_id=line_db.meter_id,
                        type_packet=line_mwl.type_packet,
                        time_detected=datetime.fromtimestamp(line_mwl.type_packet),
                        time_saved=datetime.fromtimestamp(line_mwl.type_packet),
                    )
                )
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
