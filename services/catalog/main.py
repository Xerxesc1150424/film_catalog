from fastapi import Depends, FastAPI
from sqlalchemy import select, text
from sqlalchemy.orm import Session

import models
from db import Base, SessionLocal, engine

Base.metadata.create_all(engine)

app = FastAPI(title="film_catalog")

def get_session():
    with SessionLocal() as session:
        yield session


@app.get("/health")
def health():
    return{"status": "ok"}

@app.get("/health/db")
def health_db():
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version()")).scalar()
    return {"database": "ok", "version": version}

@app.get("/films")
def list_films(
    country: str | None = None,
    decade: int | None = None,
    session: Session = Depends(get_session),
):

    query = select(models.Film)
    if country:
        query = query.join(models.FilmCountry).where(
            models.FilmCountry.country_code == country.upper()
        )
    if decade:
        query = query.where(models.Film.year >= decade, models.Film.year < decade +10)
    films = session.scalars(query.order_by(models.Film.year)).all()
    return [{"id": f.id, "title": f.title, "year": f.year} for f in films]
