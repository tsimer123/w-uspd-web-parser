from sql.model import (
    EquipmentModelGet,
    MeterModelGet,
    MeterWLHandModelGet,
    TaskEquipmentHandlerModelGet,
    TaskEquipmentModelGet,
)
from sql.scheme import Equipment, Meter, Task


def init_get_uspd(uspd: Equipment) -> EquipmentModelGet:
    temp_uspd = EquipmentModelGet(
        equipment_id=uspd.equipment_id,
        serial=uspd.serial,
        serial_in_sourse=uspd.serial_in_sourse,
        ip1=uspd.ip1,
        ip2=uspd.ip2,
        created_on=uspd.created_on,
        update_on=uspd.update_on,
    )
    return temp_uspd


def init_get_task_equipment(task: Task) -> TaskEquipmentModelGet:
    temp_uspd = TaskEquipmentModelGet(
        task_id=task.task_id,
        group_task_id=task.group_task_id,
        equipment_id=task.equipment_id,
        type_task=task.type_task,
        status_task=task.status_task,
        timeouut_task=task.timeouut_task,
        created_on=task.created_on,
        update_on=task.update_on,
        serial_in_sourse=task.equipment.serial_in_sourse,
    )
    return temp_uspd


async def init_get_task_equipment_for_handler(task: Task, time_zone: int) -> TaskEquipmentHandlerModelGet:
    temp_uspd = TaskEquipmentHandlerModelGet(
        group_task_id=task.task_id,
        task_id=task.task_id,
        equipment_id=task.equipment_id,
        type_task=task.type_task,
        status_task=task.status_task,
        timeouut_task=task.timeouut_task,
        created_on=task.created_on,
        update_on=task.update_on,
        serial_in_sourse=task.equipment.serial_in_sourse,
        ip1=task.equipment.ip1,
        ip2=task.equipment.ip2,
        login=task.equipment.login,
        passw=task.equipment.passw,
        time_zone=time_zone,
    )
    return temp_uspd


def init_get_meter(meter: Meter) -> MeterModelGet:
    temp_meter = MeterModelGet(
        meter_id=meter.meter_id,
        modem=meter.modem,
        hw_type=meter.hw_type,
    )
    return temp_meter


def init_get_meter_wl(meter: Meter) -> MeterWLHandModelGet:
    temp_meter = MeterWLHandModelGet(
        meter_id=meter.meter.meter_id,
        modem=meter.meter.modem,
        hw_type=meter.meter.hw_type,
        created_on=meter.meter.created_on,
        update_on=meter.meter.update_on,
        wl_id=meter.wl_id,
        present=meter.present,
    )
    return temp_meter


def init_get_meter_msg(meter: Meter) -> MeterModelGet:
    temp_meter = MeterModelGet(
        meter_id=meter.meter_id,
        modem=meter.modem,
        hw_type=meter.hw_type,
        wl_id=meter.messages.messages_id,
        present=meter.messages.present,
    )
    return temp_meter
