from typing import Optional, Any
from fastapi.responses import JSONResponse
from fastapi import status

def UJSONResponse(
    data: Optional[Any] = None,
    message: str = "Success",
    code: int = status.HTTP_200_OK,
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """
    Creates a JSONResponse with a unified structure.
    The `status_code` is for the HTTP response, while `code` is for the business logic status.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "data": data,
        }
    )

# Example of pre-defined responses you can use in your endpoints

def Success(data: Optional[Any] = None, message: str = "Success"):
    return UJSONResponse(data=data, message=message)

def Created(data: Optional[Any] = None, message: str = "Created"):
    return UJSONResponse(data=data, message=message, status_code=status.HTTP_201_CREATED, code=status.HTTP_201_CREATED)

def BadRequest(message: str = "Bad Request"):
    return UJSONResponse(data=None, message=message, status_code=status.HTTP_400_BAD_REQUEST, code=status.HTTP_400_BAD_REQUEST)

def Unauthorized(message: str = "Unauthorized"):
    return UJSONResponse(data=None, message=message, status_code=status.HTTP_401_UNAUTHORIZED, code=status.HTTP_401_UNAUTHORIZED)

def NotFound(message: str = "Not Found"):
    return UJSONResponse(data=None, message=message, status_code=status.HTTP_404_NOT_FOUND, code=status.HTTP_404_NOT_FOUND)

def InternalServerError(message: str = "Internal Server Error"):
    return UJSONResponse(data=None, message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, code=status.HTTP_500_INTERNAL_SERVER_ERROR)
