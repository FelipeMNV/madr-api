from fastapi import FastAPI

from madr_api.routers.auth import router as auth_router
from madr_api.routers.romancistas import router as romancistas_router
from madr_api.routers.users import router as users_router

app = FastAPI()


app.include_router(users_router)
app.include_router(auth_router)
app.include_router(romancistas_router)
