from pydantic import BaseModel, ConfigDict


class UspdEquipmentInExcel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    ip1: str
    ip2: str | None = None
    login: str = 'admin'
    passw: str = 'admin'


class EquipmentInExcel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sub_task_id: int | None = None
    uspd: UspdEquipmentInExcel
    command: str
    meters: list = []
