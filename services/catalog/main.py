from fastapi import Depends, FastAPI, HTTPException
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

@app.get("/films/{film_id}")
def get_film(film_id: int, session: Session = Depends(get_session)):
    film = session.get(models.Film, film_id)
    if film is None:
        raise HTTPException(status_code=404, detail="Film not found")

    countries = session.scalars(
        select(models.FilmCountry.country_code).where(models.FilmCountry.film_id == film_id)
    ).all()

    credits = session.execute(
        select(models.Person.id, models.Person.name, models.FilmPerson.role, models.FilmPerson.billing_order)
        .join(models.FilmPerson, models.FilmPerson.person_id == models.Person.id)
        .where(models.FilmPerson.film_id == film_id)
        .order_by(models.FilmPerson.role.desc(), models.FilmPerson.billing_order)
    ).all()

    return {
        "id": film.id,
        "title": film.title,
        "original_title": film.original_title,
        "year": film.year,
        "overview": film.overview,
        "countries": countries,
        "credits": [
            {"person_id": c.id, "name": c.name, "role": c.role, "billing_order": c.billing_order}
            for c in credits
        ],
    }

@app.get("/people/{person_id}")
def get_person(person_id: int, session: Session = Depends(get_session)):
    person = session.get(models.Person, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")

    credits = session.execute(
        select(models.Film.id, models.Film.title, models.Film.year, models.FilmPerson.role, models.FilmPerson.billing_order)
        .join(models.FilmPerson, models.FilmPerson.film_id == models.Film.id)
        .where(models.FilmPerson.person_id == person_id)
        .order_by(models.Film.year)
    ).all()

    return {
        "id": person.id,
        "name": person.name,
        "credits": [
            {"film_id": c.id, "title": c.title, "year": c.year, "role": c.role, "billing_order": c.billing_order}
            for c in credits
        ],
    }
