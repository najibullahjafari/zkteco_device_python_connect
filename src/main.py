from fastapi import FastAPI
from src.core import router

app = FastAPI()
app.include_router(router)
