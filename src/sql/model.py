from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EquipmentModelSet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    serial: int | None = None
    serial_in_sourse: str
    login: str = 'admin'
    passw: str = 'admin'
    ip1: str
    ip2: str | None = None


class EquipmentModelGet(EquipmentModelSet):
    model_config = ConfigDict(from_attributes=True)

    equipment_id: int
    created_on: datetime
    update_on: datetime


class TaskModelSet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    group_task_id: int
    equipment_id: int
    type_task: str
    status_task: str  # true/false/start
    timeouut_task: int


class TaskModelGet(TaskModelSet):
    task_id: int
    created_on: datetime
    update_on: datetime


class TaskEquipmentModelGet(TaskModelGet):
    serial_in_sourse: str


class TaskEquipmentHandlerModelGet(TaskEquipmentModelGet):
    ip1: str
    ip2: str | None
    login: str
    passw: str
    time_zone: int


class TaskModelUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: int
    group_task_id: int
    type_task: str | None = None
    status_task: str | None = None
    meter_true: str | None = None
    created_on: datetime | None = None
    update_on: datetime | None = None


class EquipmentHandModelUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    equipment_id: int
    serial: int
    bs_type: str
    mode: str
    dl_aver_busyness: int
    rev_list: str
    latitude: float
    longitude: float


class TaskHandModelUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: int
    status_task: str
    error: str | None = None
    total_time: int | None = None
    timeouut_task: int


class MeterModelSet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    modem: int
    hw_type: str | None


class MeterModelGet(MeterModelSet):
    model_config = ConfigDict(from_attributes=True)

    meter_id: int


class MeterWLHandModelGet(MeterModelGet):
    model_config = ConfigDict(from_attributes=True)

    wl_id: int
    present: bool
    created_on: datetime
    update_on: datetime


class MeterMsgHandModelGet(MeterModelGet):
    model_config = ConfigDict(from_attributes=True)

    messages_id: int
    present: bool
    created_on: datetime
    update_on: datetime


class MeterModelUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    meter_id: int
    hw_type: str


class WLModelUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    wl_id: int
    last_success: int | None = None
    present: bool


class WLModelSet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    equipment_id: int
    meter_id: int
    last_success: int
    present: bool


class MsgModelSet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    equipment_id: int
    meter_id: int
    type_packet: int
    time_detected: datetime
    time_saved: datetime


class LogHandModelSet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: int
    equipment_id: int
    status_response: bool
    response: str | None = None
