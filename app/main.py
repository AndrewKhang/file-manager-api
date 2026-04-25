from fastapi import FastAPI
from app.database import engine, Base
from app import models
from app.routers import users, files
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://snazzy-meerkat-7205c2.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(files.router)  # register file upload/download routes

@app.get("/")
def root():
    return {"message": "File Manager API"}