from fastapi import FastAPI

from models import Base

from database import engine

from routers import complaints
from routers import dashboard
from routers import admin

Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="CivicAssist AI"
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