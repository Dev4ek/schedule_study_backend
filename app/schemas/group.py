from pydantic import BaseModel, Field


class group_id(BaseModel):
    group_id: int = Field(..., title="id группы", description="id группы в базе даннных", examples=[2])
    
class info_group(BaseModel):
    group_id: int = Field(..., title="id группы", description="id группы в базе даннных", examples=[2])
    group: str = Field(...,  title="Группа", examples=["Исп-232", "Исп-211"])
    