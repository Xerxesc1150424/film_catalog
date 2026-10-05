import csv
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

import models
from db import Base, SessionLocal, engine

load_dotenv()
API_KEY = os.environ["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
CSV_PATH = Path(__file__).parent / "data" / "seed_films.csv"

def tmdb_get(path, **params):
    params["api_key"] = API_KEY
    response = requests.get(f"{BASE_URL}{path}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def find_tmdb_id(title, year):
    results = tmdb_get("/search/movie", query=title, year=year)["results"]
    if not results:
        return None
    return results[0]["id"]

def get_or_create_person(session, tmdb_id, name):
    person = session.query(models.Person).filter_by(tmdb_id=tmdb_id).first()
    if person is None:
        person = models.Person(tmdb_id=tmdb_id, name=name)
        session.add(person)
        session.flush()
    return person

def save_film(session, data):
    year = int(data["release_date"][:4]) if data.get("release_date") else None
    film = models.Film(
        tmdb_id=data["id"],
        title=data["title"],
        original_title=data.get("original_title"),
        year=year,
        overview=data.get("overview"),
    )
    session.add(film)
    session.flush()

    for country in data["production_countries"]:
        code = country["iso_3166_1"]
        if session.get(models.Country, code) is None:
            session.add(models.Country(code=code, name=country["name"]))
            session.flush()
        session.add(models.FilmCountry(film_id=film.id, country_code=code))

    for crew in data["credits"]["crew"]:
        if crew["job"] == "Director":
            person = get_or_create_person(session, crew["id"], crew["name"])
            session.add(models.FilmPerson(film_id=film.id, person_id=person.id, role="director"))

    for position, cast in enumerate(data["credits"]["cast"][:3], start=1):
        person = get_or_create_person(session, cast["id"], cast["name"])
        session.add(
            models.FilmPerson(
                film_id=film.id, person_id=person.id, role="actor", billing_order=position
            )
        )



def main():
    Base.metadata.create_all(engine)
    with SessionLocal() as session, open(CSV_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            tmdb_id = find_tmdb_id(row["title"], row["year"])
            if tmdb_id is None:
                print(f"NOT FOUND  {row['title']} ({row['year']})")
                continue
            if session.query(models.Film).filter_by(tmdb_id=tmdb_id).first():
                print(f"SKIP       {row['title']} (already saved)")
                continue
            data = tmdb_get(f"/movie/{tmdb_id}", append_to_response="credits")
            save_film(session, data)
            session.commit()
            print(f"SAVED      {data['title']} ({year_of(data)})")
            time.sleep(0.25)


def year_of(data):
    return (data.get("release_date") or "")[:4]


if __name__ == "__main__":
    main()
