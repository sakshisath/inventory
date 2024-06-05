from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import uvicorn

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Integer)
    quantity = Column(Integer)

# Pydantic Schemas
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

# CRUD operations
def get_item(db: Session, item_id: int):
    return db.query(Item).filter(Item.id == item_id).first()

def get_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Item).offset(skip).limit(limit).all()

def search_items(db: Session, name: str):
    return db.query(Item).filter(Item.name.contains(name)).all()

def create_item(db: Session, item: ItemCreate):
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, item_id: int, item: ItemUpdate):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item:
        for key, value in item.dict().items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        update_item_ids(db)
    return db_item

def update_item_ids(db: Session):
    items = db.query(Item).order_by(Item.id).all()
    for index, item in enumerate(items):
        item.id = index + 1
    db.commit()

# FastAPI app
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API routes
@app.post("/items/", response_model=ItemResponse)
def create_item_endpoint(item: ItemCreate, db: Session = Depends(get_db)):
    return create_item(db=db, item=item)

@app.get("/items/", response_model=list[ItemResponse])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = get_items(db, skip=skip, limit=limit)
    return items

@app.get("/items/{item_id}", response_model=ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.get("/search/", response_model=list[ItemResponse])
def search_items_endpoint(name: str, db: Session = Depends(get_db)):
    items = search_items(db, name=name)
    return items

@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item_endpoint(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    db_item = update_item(db, item_id, item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.delete("/items/{item_id}", response_model=ItemResponse)
def delete_item_endpoint(item_id: int, db: Session = Depends(get_db)):
    db_item = delete_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
