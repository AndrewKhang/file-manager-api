from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app import models
from app.routers import users, files

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(files.router)  # register file upload/download routes

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")