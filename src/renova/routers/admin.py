from fastapi import APIRouter

router = APIRouter(prefix="/admin")


@router.get("/")
async def read_admin():
    return [{"admin_id": 0}]


@router.get("/therapist")
async def get_therapists():
    # get list of therapits from db
    # render html using list of therapists
    # return rendered html
    pass
