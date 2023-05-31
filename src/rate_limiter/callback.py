from math import ceil

from fastapi import HTTPException
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import Response

from src.config import RATE_LIMITER_FLAG


async def custom_callback(request: Request, response: Response, pexpire: int):
    """
    default callback when too many requests
    :param request:
    :param pexpire: The remaining milliseconds
    :param response:
    :return:
    """
    rate_limiter_flag = request.headers.get("Rate-Limiter-Flag")
    if rate_limiter_flag == RATE_LIMITER_FLAG:
        return

    expire = ceil(pexpire / 1000)

    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=f"Too many requests. Please try again after {expire} seconds.",
        headers={"Retry-After": str(expire)}
    )
