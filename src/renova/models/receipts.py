from datetime import datetime
from typing import Annotated

from sqlmodel import Field, Relationship, SQLModel


class InventoryReceiptItem(SQLModel, table=True):
    id: Annotated[int, Field(primary_key=True)]
    receipt: "InventoryReceipt" = Relationship(back_populates="items") # workaround https://github.com/fastapi/sqlmodel/issues/229
    name: str
    count: int
    price: int
    supplier_name: str


class InventoryReceipt(SQLModel, table=True):
    id: Annotated[int, Field(primary_key=True)]
    date: datetime
    total_cost: int
    store_name: str
    items: Annotated[list[InventoryReceiptItem], Relationship(back_populates="receipt")] # workaround https://github.com/fastapi/sqlmodel/issues/229
