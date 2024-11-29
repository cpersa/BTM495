from typing import Annotated
from sqlmodel import Field, SQLModel


class InventoryProduct(SQLModel, table=True):
    id: Annotated[int | None, Field(primary_key=True)] = None
    name: Annotated[str, Field(unique=True)]
    quantity: int
    supplier: str
    price: int

    def add(self, quantity: int):
        self.quantity += quantity

    @property
    def total(self):
        return self.quantity * self.price
