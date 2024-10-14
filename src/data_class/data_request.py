from pydantic import BaseModel, ConfigDict


class GetResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: bool
    data: str | None = None
    error: list | None = None


class ResultRequestModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name_uspd: str
    host: str
    status_connect: bool
    status_conf: bool
    result: str | list
    error: list
    command: str
    api: str
    time_uspd_utc: str
    statr_ver_fw: str
