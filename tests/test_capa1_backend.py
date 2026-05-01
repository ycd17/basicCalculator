import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from services.calculator import sumar, ErrorExpresion



def test_B_01_01_suma_dos_enteros():
    assert sumar('3 + 5') == 8.0

def test_B_01_02_suma_tres_numeros():
    assert sumar('1 + 2 + 3') == 6.0

def test_B_01_03_suma_con_decimales():
    assert sumar('1.5 + 2.5') == pytest.approx(4.0)

def test_B_01_04_numeros_grandes():
    assert sumar('1000 + 2000 + 3000') == 6000.0

def test_B_01_05_un_solo_numero():
    assert sumar('42') == 42.0

def test_B_01_06_cero_mas_cero():
    assert sumar('0 + 0') == 0.0

def test_B_01_07_espacios_extra():
    assert sumar('  3  +  5  ') == 8.0

def test_B_02_01_limite_200_chars_valido():
    # 50 unos separados por ' + ' = 197 chars, ljust rellena hasta 200
    expr = (' + '.join(['1'] * 50)).ljust(200)
    assert len(expr) == 200
    assert sumar(expr) == pytest.approx(50.0)

def test_B_02_02_limite_201_chars_invalido():
    with pytest.raises(ErrorExpresion):
        sumar('1' * 201)

@pytest.mark.parametrize("expresion, caso", [
    ('',                                    'B-03-01 vacía'),
    ('   ',                                 'B-03-02 solo espacios'),
    ('3 ++ 5',                              'B-03-03 operadores consecutivos'),
    ('+ 3 + 5',                             'B-03-04 empieza con +'),
    ('3 + 5 +',                             'B-03-05 termina con +'),
    ('3 * 5',                               'B-03-06 multiplicación'),
    ('10 - 3',                              'B-03-07 resta'),
    ('tres + cinco',                        'B-03-08 letras'),
    ("__import__('os').system('ls')",       'B-03-09 inyección de código'),
])
def test_B_03_invalidos(expresion, caso):
    with pytest.raises(ErrorExpresion):
        sumar(expresion)

def test_B_03_10_tipo_int():
    with pytest.raises(ErrorExpresion):
        sumar(42)

def test_B_03_11_tipo_none():
    with pytest.raises(ErrorExpresion):
        sumar(None)

@pytest.mark.parametrize("dato, esperado", [
    ('0 + 0',             0.0),
    ('10 + 20',          30.0),
    ('100 + 200 + 300',  600.0),
    ('0.5 + 0.5',          1.0),
    ('999 + 1',          1000.0),
])
def test_B_04_validos_parametricos(dato, esperado):
    assert sumar(dato) == pytest.approx(esperado)

@pytest.mark.parametrize("dato", [
    'abc',
    '1 + 2 + ',
    '/5',
    '1 ++ 2',
    '.',
])
def test_B_04_invalidos_parametricos(dato):
    with pytest.raises(ErrorExpresion):
        sumar(dato)


def test_B_EX_01_flotante_impreciso():
    assert sumar('0.1 + 0.2') == pytest.approx(0.3)

def test_B_EX_02_numero_muy_grande():
    assert sumar('999999 + 1') == 1000000.0

def test_B_EX_03_decimal_mal_puesto():
    with pytest.raises(ErrorExpresion):
        sumar('3. + 5')
