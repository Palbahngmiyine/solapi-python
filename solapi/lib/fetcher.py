from enum import Enum
from typing import Any, TypedDict, TypeVar

import httpx
from httpx import Response

from solapi.lib.authenticator import AuthenticationParameter, Authenticator


class RequestMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class RequestType(TypedDict):
    method: RequestMethod
    url: str


T = TypeVar("T")
R = TypeVar("R")


async def default_fetcher(
    auth_parameter: AuthenticationParameter,
    request: RequestType,
    data: T | None = None,
) -> R:
    """

    Args:
        auth_parameter: API Key, Api Secret Key Dictionary. 반드시 활성화된 유효한 API Key, API Secret Key를 입력하셔야 합니다.
        request: HTTP Request를 위한 파라미터, 정확한 API URL, HTTP Method를 입력해주세요!
        data: 발송 혹은 API 요청 시 전달해야 할 파라미터 목록, HTTP GET API를 이용하면 None 타입으로 지정됩니다.

    Returns:
        정상 작동할 경우 JSON 데이터를 반환합니다.
    """
    authorization_header_data = Authenticator(
        auth_parameter["api_key"], auth_parameter["api_secret"]
    ).get_auth_info()
    headers = {
        "Authorization": authorization_header_data,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response: Response = await client.request(
            method=request["method"], url=request["url"], headers=headers, json=data
        )

    # 4xx 에러 처리: 클라이언트 오류일 경우
    # TODO: Custom Error 만들어야 함
    if 400 <= response.status_code < 500:
        error_response: dict[str, Any] = response.json()
        raise Exception(
            error_response.get("errorCode", "UnknownError"),
            error_response.get("errorMessage", ""),
        )
    # 5xx 에러 처리: 서버 오류일 경우
    elif response.status_code >= 500:
        raise Exception("UnknownError", response.text)

    try:
        return response.json()
    except Exception as exc:
        raise Exception(response.text) from exc
