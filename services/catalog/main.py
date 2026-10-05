from fastapi import FastAPI
from sqlalchemy import text

from db import engine

app = FastAPI(title="film_catalog")


@app.get("/health")
def health():
    return{"status": "ok"}

@app.get("/health/db")
def health_db():
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version()")).scalar()
    return {"database": "ok", "version": version}
