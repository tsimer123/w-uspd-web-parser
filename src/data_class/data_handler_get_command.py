from pydantic import BaseModel, ConfigDict


class WlHandModelSet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    equipment_id: int
    number: int
    last_success: int
    present: bool
