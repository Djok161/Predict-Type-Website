from fastapi import FastAPI
from starlette.responses import RedirectResponse

from controll.endpoint import type_router

app = FastAPI()

app.include_router(type_router)


@app.get("/")
def redirect():
	return RedirectResponse("/docs")
