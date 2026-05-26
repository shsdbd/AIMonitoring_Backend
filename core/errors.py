from typing import Any

from fastapi import HTTPException, status


class AppError(HTTPException):
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        detail: Any | None = None,
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail={
                "error_code": error_code,
                "message": message,
                "detail": detail,
            },
        )


def bad_request(error_code: str, message: str, detail: Any | None = None) -> AppError:
    return AppError(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_code=error_code,
        message=message,
        detail=detail,
    )


def not_found(error_code: str, message: str, detail: Any | None = None) -> AppError:
    return AppError(
        status_code=status.HTTP_404_NOT_FOUND,
        error_code=error_code,
        message=message,
        detail=detail,
    )


def unprocessable_entity(
    error_code: str,
    message: str,
    detail: Any | None = None,
) -> AppError:
    return AppError(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code=error_code,
        message=message,
        detail=detail,
    )


def service_unavailable(
    error_code: str,
    message: str,
    detail: Any | None = None,
) -> AppError:
    return AppError(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        error_code=error_code,
        message=message,
        detail=detail,
    )
