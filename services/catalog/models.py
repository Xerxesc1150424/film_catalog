from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db import Base

class Country(Base):
    __tablename__ = "countries"

    code: Mapped[str] = mapped_column(String(2), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

class Film(Base):
    __tablename__ = "films"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tmdb_id: Mapped[int] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column(String(300))
    year: Mapped[int | None]
    overview: Mapped[str | None] = mapped_column(Text)

class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    tmdb_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(String(200))

class FilmCountry(Base):
    __tablename__ = "film_countries"
   
    film_id: Mapped[int] = mapped_column(ForeignKey("films.id"), primary_key=True)
    country_code: Mapped[str] = mapped_column(ForeignKey("countries.code"), primary_key=True)

class FilmPerson(Base):
    __tablename__ = "film_people"
    
    film_id: Mapped[int] = mapped_column(ForeignKey("films.id"), primary_key=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), primary_key=True)
    role: Mapped[str] = mapped_column(String(20), primary_key=True)
    billing_order: Mapped[int | None]
