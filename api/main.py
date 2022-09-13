from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .routers.files import router

from .handlers.files import ExceptionWithMessage


app = FastAPI()

app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"message": "Validation Failed"})


@app.exception_handler(ExceptionWithMessage)
async def exception_handler(request: Request, exc: ExceptionWithMessage):
    return JSONResponse(status_code=exc.code, content={"message": exc.message})
