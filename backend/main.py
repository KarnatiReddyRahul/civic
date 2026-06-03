from database import engine
from fastapi import FastAPI
from models import Base
from routers import admin, complaints, dashboard

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