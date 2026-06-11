from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine
from backend.models import Base
from backend.routers import admin, complaints, dashboard

Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="CivicAssist AI"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    complaints.router,
    prefix="/api/complaints"
)

app.include_router(
    dashboard.router,
    prefix="/api/dashboard"
)

app.include_router(
    admin.router,
    prefix="/api/admin"
)

@app.get("/")
def root():

    return {
        "message":
        "CivicAssist AI Backend Running"
    }