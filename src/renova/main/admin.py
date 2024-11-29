import csv
from collections import defaultdict
from datetime import date, datetime
from io import StringIO
from typing import IO, Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlmodel import select

from renova.context import Context, get_context
from renova.credentials import authenticate
from renova.main.templates import templates
from renova.models.products import InventoryProduct
from renova.models.receipts import InventoryReceipt
from renova.models.therapists import StatusOfWork, Therapist


class OwnerContext(Context):
    def get_unconfirmed_therapists(self):
        return self.session.exec(
            select(Therapist).where(Therapist.status_of_work == StatusOfWork.pending)
        ).all()

    def confirm_therapist(self, therapist: Therapist, status: StatusOfWork):
        therapist.confirm(status)
        self.session.add(therapist)
        self.session.commit()

    def add_product(self, name: str, quantity: int, supplier: str, price: int):
        inventory_product = InventoryProduct(
            name=name, quantity=quantity, supplier=supplier, price=price
        )
        self.session.add(inventory_product)
        self.session.commit()
        self.session.refresh(inventory_product)
        return inventory_product

    def adjust_product_quantity(self, name, count: int):
        inventory_product = self.session.exec(
            select(InventoryProduct).where(InventoryProduct.name == name)
        ).one()
        inventory_product.add(count)
        self.session.add(inventory_product)
        self.session.commit()

    def generate_inventory_report(self) -> IO[str]:
        f = StringIO()
        writer = csv.writer(f)
        writer.writerows(
            self.session.exec(
                select(
                    InventoryProduct.name,
                    func.sum(InventoryProduct.quantity),
                ).group_by(InventoryProduct.name)
            ).all()
        )
        return f

    def generate_expense_report(self, start_date: date, end_date: date) -> IO[str]:
        receipts = self.session.exec(
            select(InventoryReceipt).where(
                start_date <= InventoryReceipt.date and InventoryReceipt.date < end_date
            )
        ).all()
        expenses = defaultdict(lambda: 0)
        for receipt in receipts:
            for item in receipt.items:
                expenses[item.name] += item.count * item.price

        f = StringIO()
        csv.writer(f).writerows(expenses.items())
        return f


router = APIRouter(prefix="/admin")


@router.get("", dependencies=[Depends(authenticate(required=True))])
def get_admin_dashboard(
    request: Request,
):
    return templates.TemplateResponse(request, "pages/admin.html")


@router.get("/inventory_report")
def get_report(
    ctx: Annotated[OwnerContext, Depends(get_context(OwnerContext, auth=True))],
):
    def stream():
        with ctx.generate_inventory_report() as f:
            yield from f

    return StreamingResponse(
        content=stream(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={datetime.now().isoformat(sep="T", timespec="seconds")}.csv"
        },
    )
