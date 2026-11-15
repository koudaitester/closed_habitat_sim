from pydantic import BaseModel, Field
class PlantClassifyReq(BaseModel):
    image_b64: str = Field(..., min_length=1, description="图片base64，非空")
    tag: str | None = None
class PlantClassifyResp(BaseModel):
    type_id: int
    desc: str
    advice: str
    warning: str
