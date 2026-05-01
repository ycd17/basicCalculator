import re

_PATRON_NUMERO = re.compile(r'^\d+(\.\d+)?$')


class ErrorExpresion(ValueError):
    pass


def sumar(dato: str) -> float:
    _validar_string(dato)
    partes = [p.strip() for p in dato.strip().split('+')]
    _validar_partes(partes)
    return sum(float(p) for p in partes)


def _validar_string(dato: str) -> None:
    if not isinstance(dato, str):
        raise ErrorExpresion("La expresión debe ser un string")
    if len(dato) > 200:
        raise ErrorExpresion("La expresión supera los 200 caracteres permitidos")
    stripped = dato.strip()
    if not stripped:
        raise ErrorExpresion("La expresión no puede estar vacía")
    if not re.fullmatch(r'[\d\s.+]+', dato):
        raise ErrorExpresion("Solo se permiten dígitos, '+', '.' y espacios")
    if stripped.startswith('+') or stripped.endswith('+'):
        raise ErrorExpresion("La expresión no puede empezar ni terminar con '+'")


def _validar_partes(partes: list[str]) -> None:
    for parte in partes:
        if not _PATRON_NUMERO.match(parte):
            raise ErrorExpresion(f"Número inválido: '{parte}'")
