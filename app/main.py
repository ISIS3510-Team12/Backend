from fastapi import FastAPI

app = FastAPI(title="Back-end")


@app.get("/")
def root() -> dict:
    return {"message": "Hola :)"}
