from auth import get_current_user
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


class ApiKeyVerifyResponse(BaseModel):
    valid: bool
    user_id: int
    username: str
    message: str


@router.get("/verify", response_model=ApiKeyVerifyResponse, summary="Verify API key")
def verify_api_key_endpoint(current_user: dict = Depends(get_current_user)):
    return ApiKeyVerifyResponse(
        valid=True,
        user_id=current_user["user_id"],
        username=current_user["username"],
        message="API key válida",
    )
