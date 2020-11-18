from fastapi import FastAPI
from stac_item.routes import stac_router
from config import config
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    stac_router,
    prefix="/stac",
    tags=["stac"],
    responses={404: {"description": "Not found"}},
)

@app.on_event("startup")
async def app_startup():
    """
    Do tasks related to app initialization.
    """
    config.load_config()

@app.on_event("shutdown")
async def app_shutdown():
    """
    Do tasks related to app termination.
    """
    config.close_db_client()