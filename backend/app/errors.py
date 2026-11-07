"""Errors as RFC 9457 problem details (application/problem+json), plus the
406/415 content negotiation checks required by the API contract."""

from collections.abc import Awaitable, Callable, Mapping
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import settings

PROBLEM_JSON = "application/problem+json"
# Accept ranges a JSON response satisfies.
JSON_RANGES = {"*/*", "application/*", "application/json", PROBLEM_JSON}
# HTML pages; they don't produce JSON.
NEGOTIATION_EXEMPT = {f"{settings.API_STR}/docs", f"{settings.API_STR}/redoc"}


class ProblemError(BaseModel):
    field: str
    message: str


class Problem(BaseModel):
    """Error description per RFC 9457 (Problem Details for HTTP APIs)."""

    type: str = "about:blank"
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    errors: list[ProblemError] | None = Field(
        default=None, description="Validation errors of individual fields"
    )


def problem_response(
    status_code: int,
    detail: str | None = None,
    *,
    instance: str | None = None,
    errors: list[ProblemError] | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    problem = Problem(
        title=HTTPStatus(status_code).phrase,
        status=status_code,
        detail=detail,
        instance=instance,
        errors=errors,
    )
    return JSONResponse(
        problem.model_dump(exclude_none=True),
        status_code=status_code,
        media_type=PROBLEM_JSON,
        headers=headers,
    )


def problems(*codes: int) -> dict[int | str, dict[str, Any]]:
    """OpenAPI `responses` entries for error codes a route can return."""
    return {
        code: {"model": Problem, "description": HTTPStatus(code).phrase}
        for code in codes
    }


# Syntax errors -> 400; values that parse but break a rule (range, length,
# pattern, min < max) -> 422.
def _is_syntax_error(error: dict[str, Any]) -> bool:
    kind: str = error["type"]
    return (
        error["loc"][0] != "body"
        or kind in ("json_invalid", "missing", "extra_forbidden")
        or kind.endswith(("_type", "_parsing"))
    )


def _field(loc: tuple[int | str, ...]) -> str:
    path = loc[1:] if len(loc) > 1 else loc
    return ".".join(str(part) for part in path)


async def _validation_handler(request: Request, exc: Exception) -> Response:
    assert isinstance(exc, RequestValidationError)
    raw = list(exc.errors())
    errors = [ProblemError(field=_field(e["loc"]), message=e["msg"]) for e in raw]
    syntax = any(_is_syntax_error(e) for e in raw)
    return problem_response(
        status.HTTP_400_BAD_REQUEST
        if syntax
        else status.HTTP_422_UNPROCESSABLE_CONTENT,
        # A readable one-liner for clients that only show `detail`.
        "; ".join(f"{e.field}: {e.message}" for e in errors),
        instance=request.url.path,
        errors=errors,
    )


async def _http_handler(request: Request, exc: Exception) -> Response:
    assert isinstance(exc, StarletteHTTPException)
    if exc.status_code < 400:
        return Response(status_code=exc.status_code, headers=exc.headers)
    detail = exc.detail if isinstance(exc.detail, str) else None
    return problem_response(
        exc.status_code, detail, instance=request.url.path, headers=exc.headers
    )


async def _unhandled_handler(request: Request, exc: Exception) -> Response:
    return problem_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR, instance=request.url.path
    )


def _media_type(value: str) -> str:
    return value.split(";", 1)[0].strip().lower()


def _accepts_json(accept: str) -> bool:
    for item in accept.split(","):
        media, *params = (part.strip() for part in item.split(";"))
        q = next((p[2:] for p in params if p.lower().startswith("q=")), "1")
        try:
            if float(q) == 0:
                continue
        except ValueError:
            pass
        if media.lower() in JSON_RANGES or media.lower().endswith("+json"):
            return True
    return False


def _is_json(content_type: str) -> bool:
    media = _media_type(content_type)
    return media == "application/json" or (
        media.startswith("application/") and media.endswith("+json")
    )


async def _negotiation_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    path = request.url.path
    if path.startswith(settings.API_STR) and path not in NEGOTIATION_EXEMPT:
        accept = request.headers.get("accept", "").strip()
        if accept and not _accepts_json(accept):
            return problem_response(
                status.HTTP_406_NOT_ACCEPTABLE,
                "Only application/json responses are available",
                instance=path,
            )
        has_body = (
            int(request.headers.get("content-length") or 0) > 0
            or "transfer-encoding" in request.headers
        )
        if has_body and not _is_json(request.headers.get("content-type", "")):
            return problem_response(
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                "Request body must be application/json",
                instance=path,
            )
    return await call_next(request)


def _fix_openapi(schema: dict[str, Any]) -> dict[str, Any]:
    """Errors are documented as application/problem+json; FastAPI's own
    HTTPValidationError is replaced by Problem."""
    for path_item in schema.get("paths", {}).values():
        for operation in path_item.values():
            responses: dict[str, Any] = operation.get("responses", {})
            default_422 = responses.get("422", {})
            if "HTTPValidationError" in str(default_422):
                del responses["422"]
                responses.setdefault(
                    "400",
                    {
                        "description": HTTPStatus(400).phrase,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Problem"}
                            }
                        },
                    },
                )
            for code, response in responses.items():
                content = response.get("content", {})
                if int(code) >= 400 and "application/json" in content:
                    content[PROBLEM_JSON] = content.pop("application/json")
    components = schema.get("components", {}).get("schemas", {})
    components.pop("HTTPValidationError", None)
    components.pop("ValidationError", None)
    return schema


def setup_errors(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, _validation_handler)
    app.add_exception_handler(StarletteHTTPException, _http_handler)
    app.add_exception_handler(Exception, _unhandled_handler)
    app.middleware("http")(_negotiation_middleware)

    original_openapi = app.openapi

    def openapi() -> dict[str, Any]:
        if app.openapi_schema is None:
            app.openapi_schema = _fix_openapi(original_openapi())
        return app.openapi_schema

    app.openapi = openapi  # type: ignore[method-assign]
