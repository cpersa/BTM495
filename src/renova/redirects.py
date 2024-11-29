from fastapi import Request, Response
from fastapi.datastructures import URL
from fastapi.responses import RedirectResponse
from pydantic import HttpUrl


def redirect(request: Request, status_code: int, location: str | URL | HttpUrl):
    if "HX-Request" in request.headers and (status_code < 300 or 400 <= status_code):
        return Response(status_code=status_code, headers={"HX-Location": str(location)})
    else:
        if status_code < 300 or 400 <= status_code:
            status_code = 303
        return RedirectResponse(str(location), status_code=status_code)
