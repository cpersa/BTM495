from fastapi import APIRouter

router = APIRouter(prefix="/admin")


@router.get("/")
async def read_admin():
    return [{"admin_id": 0}]
