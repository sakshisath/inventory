from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    description: str
    price: int
    quantity: int

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int

    class Config:
        orm_mode = True