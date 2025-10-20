from fastapi import APIRouter

router = APIRouter()

@router.post("/register", status_code=201)
async def register():
    return {"message": "register route"}