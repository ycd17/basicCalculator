import pytest
from services.calculator import sumar


@pytest.mark.parametrize("dato, esperado", [
    ("1+2",           3),
    ("10+20",        30),
    ("112+21",      133),   # números compuestos
    ("1+2+3+4+5",    15),   # múltiples operandos
    ("0+0",           0),
    ("5",             5),   # operando único
    ("100+200+300",  600),
    ("999+1",       1000),
])
def test_sumar_parametrizado(dato, esperado):
    assert sumar(dato) == esperado


def test_sumar_con_espacios_alrededor():
    assert sumar("1 + 2") == 3


def test_sumar_lanza_error_con_letras():
    with pytest.raises(ValueError):
        sumar("1+abc")
