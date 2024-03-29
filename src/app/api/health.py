import asyncio
import socket

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session

router = APIRouter(
    prefix="/health", dependencies=[Depends(get_async_session)], tags=["Health"]
)


@router.get(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Database connection is unavailable",
        }
    },
)
async def health(
    session: AsyncSession = Depends(get_async_session),
) -> Response:
    try:
        #  SELECT 1 is a simple SQL query used to test database connectivity
        await asyncio.wait_for(session.execute(select(1)), timeout=1)
    except (asyncio.TimeoutError, socket.gaierror):
        #  socket.gaierror exception is raised when there is an error resolving a hostname. In this case,
        #  it is being used to handle network-related errors that may occur when attempting to connect to the database
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(status_code=204)
