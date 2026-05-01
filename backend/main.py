import os

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from services.calculator import sumar, ErrorExpresion

app = FastAPI(title="Calculadora API")


class SumaRequest(BaseModel):
    dato: str


class SumaResponse(BaseModel):
    resultado: float


@app.post("/sumar", response_model=SumaResponse)
def sumar_endpoint(req: SumaRequest) -> SumaResponse:
    try:
        return SumaResponse(resultado=sumar(req.dato))
    except ErrorExpresion as e:
        status = 400 if not req.dato.strip() else 422
        raise HTTPException(status_code=status, detail=str(e))


_frontend = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=_frontend, html=True), name="frontend")
