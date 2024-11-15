from datetime import datetime
from typing import Annotated

from sqlmodel import Field, Relationship, SQLModel


class InventoryReceiptItem(SQLModel, table=True):
    id: Annotated[int | None, Field(default=None, primary_key=True)]
    receipt_id: Annotated[
        int | None, Field(default=None, foreign_key="inventoryreceipt.id")
    ]
    receipt: "InventoryReceipt" = Relationship(back_populates="items")
    name: str
    count: int
    price: int
    supplier_name: str


class InventoryReceipt(SQLModel, table=True):
    id: Annotated[int | None, Field(default=None, primary_key=True)]
    date: datetime
    total_cost: int
    store_name: str
    items: list[InventoryReceiptItem] = Relationship(back_populates="receipt")


class ExpenseReport(SQLModel, table=True):
    id: Annotated[int | None, Field(default=None, primary_key=True)]
    date: datetime
    itemName: str
    itemCount: int
    supplierName: str


class Destination(SQLModel, table=True):
    id: Annotated[int | None, Field(default=None, primary_key=True)]
    destinationName: str
    storageType: str
    availableSpace: str
