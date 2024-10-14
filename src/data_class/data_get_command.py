from pydantic import BaseModel, ConfigDict


class TaskGetModel(BaseModel):
    """Сохраняем результат http запроса"""

    model_config = ConfigDict(from_attributes=True)

    status: bool
    error: str | None = None
    task_id: int | None = None


class ListTaskModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: int
    meter_id: int | None = None
    status_task_db: str = 'wait'  # true/false/wait
    response: dict | None = None
    status_hand: bool = False
    error: str | None = None


# class TaskHandModel(BaseModel):
#     """Сохраняем результат обработки таски"""

#     model_config = ConfigDict(from_attributes=True)

#     status: bool
#     error: str | None = None
#     task_id: str | None = None


class MeterWlModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    number: int
    hw_type: str
    last_success_dl_ts: int


class MeterPacketModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uspd_serial: int
    meter_number: int
    type_packet: int
    time_detected: int
    time_saved: int


class MeterWlAllModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: bool
    error: str | None = None
    meter_wl: list[MeterWlModel] | None = None


class MeterPacketAllModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: bool
    error: str | None = None
    meter_packet: list[MeterPacketModel] | None = None


class EquipmentInfoModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: bool
    error: str | None = None
    serial: int | None = None
    bs_type: str | None = None
    mode: str | None = None
    dl_aver_busyness: int | None = None
    rev_list: str | None = None
    latitude: str | None = None
    longitude: str | None = None


class GetComandModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: int
    equipment_id: int
    type_task: str
    status_task: str
    meter_wl: MeterWlAllModel | None = None
    meter_packet: MeterPacketAllModel | None = None
    equipment_info: EquipmentInfoModel | None = None
    error: str | None = None
    total_time: int | None = None


class GetResultTaskModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: bool
    error: str | None = None
    data: dict | None = None


class StatusHandModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: bool = False
    list_task: list[ListTaskModel]
    error: str | None = None
