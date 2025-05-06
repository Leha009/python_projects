import functools
import os

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, FileResponse

from custom_logger import Logger
from utils import *

logger = Logger(
    name="API",
    filename="requests.log",
    filemode="a+"
)

app = FastAPI()

@app.get("/versions")
def get_versions(request: Request, app: str) -> Response:
    client_ip = request.client.host
    logger.info(f"{client_ip} wanted to see versions of {app}")
    if not os.path.exists(f"{UPDATE_DIR}/{app}"):
        return JSONResponse(content={"detail": "not found"}, status_code=404)

    last_version = ""
    available_versions = list()
    for file in os.listdir(f"{UPDATE_DIR}/{app}"):
        if not file.endswith(UPDATE_FILE_EXT):
            continue

        file_version = os.path.basename(file).removesuffix(UPDATE_FILE_EXT)
        available_versions.append(file_version)
        last_version = get_higher_version(file_version, last_version)

    available_versions.sort(key=functools.cmp_to_key(compare_version), reverse=True)
    return JSONResponse(
        content={
            "last_version": last_version,
            "versions": available_versions
        }
    )

@app.get("/get_version")
def get_file_version(
    request: Request, app: str, version: str
) -> Response:
    client_ip = request.client.host
    logger.info(f"{client_ip} is downloading {app} v{version}")
    file_path = get_app_file_version_path(app, version)
    if file_path is None:
        return JSONResponse(content={"detail": "not found"}, status_code=404)

    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=os.path.basename(file_path)
    )
