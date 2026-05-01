import os

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from services.calculator import sumar

app = FastAPI(title="Calculadora API")


class SumaRequest(BaseModel):
    dato: str


class SumaResponse(BaseModel):
    resultado: int


@app.post("/sumar", response_model=SumaResponse)
def sumar_endpoint(req: SumaRequest) -> SumaResponse:
    if not req.dato.strip():
        raise HTTPException(status_code=400, detail="El campo dato no puede estar vacío")
    try:
        return SumaResponse(resultado=sumar(req.dato))
    except ValueError:
        raise HTTPException(status_code=422, detail="Formato inválido: solo se permiten números separados por '+'")


_frontend = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=_frontend, html=True), name="frontend")
