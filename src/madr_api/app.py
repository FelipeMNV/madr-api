from fastapi import FastAPI

from madr_api.routers.users import router as users_router

app = FastAPI()


app.include_router(users_router)
