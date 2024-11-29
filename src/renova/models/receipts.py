from datetime import date
from typing import Annotated

from sqlmodel import Field, Relationship, SQLModel


class InventoryReceiptItem(SQLModel, table=True):
    id: Annotated[int | None, Field(default=None, primary_key=True)] = None
    receipt_id: Annotated[
        int | None, Field(default=None, foreign_key="inventoryreceipt.id")
    ]
    receipt: "InventoryReceipt" = Relationship(back_populates="items")
    name: str
    count: int
    price: int
    supplier_name: str


class InventoryReceipt(SQLModel, table=True):
    id: Annotated[int | None, Field(default=None, primary_key=True)] = None
    date: date
    store_name: str
    items: list[InventoryReceiptItem] = Relationship(back_populates="receipt")

    @property
    def total(self):
        return sum(item.count * item.price for item in self.items)
