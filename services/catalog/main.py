from fastapi import FastAPI

app = FastAPI(title="film_catalog")


@app.get("/health")
def health():
    return{"status": "ok"}
