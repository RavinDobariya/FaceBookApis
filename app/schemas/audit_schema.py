from pydantic import BaseModel

class AuditCreate(BaseModel):
    action: str
    entity_id: str
    user_id: str