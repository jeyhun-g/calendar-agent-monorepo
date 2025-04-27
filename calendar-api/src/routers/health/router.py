from fastapi import APIRouter, status 

router = APIRouter(prefix="/health", tags=["health"])

@router.get("", status_code=status.HTTP_200_OK)
async def health():
    return {"service_name": "calendar_api", "status": "okay"}