import pytest


class TestSumarExitoso:
    def test_suma_basica(self, api_client):
        r = api_client.post("/sumar", json={"dato": "1+2"})
        assert r.status_code == 200
        assert r.json() == {"resultado": 3}

    def test_numero_compuesto(self, api_client):
        r = api_client.post("/sumar", json={"dato": "112+21"})
        assert r.status_code == 200
        assert r.json()["resultado"] == 133

    def test_multiples_operandos(self, api_client):
        r = api_client.post("/sumar", json={"dato": "1+2+3+4+5"})
        assert r.status_code == 200
        assert r.json()["resultado"] == 15

    def test_operando_unico(self, api_client):
        r = api_client.post("/sumar", json={"dato": "42"})
        assert r.status_code == 200
        assert r.json()["resultado"] == 42

    def test_suma_con_cero(self, api_client):
        r = api_client.post("/sumar", json={"dato": "0+0"})
        assert r.status_code == 200
        assert r.json()["resultado"] == 0


class TestSumarErrores:
    def test_dato_vacio_retorna_400(self, api_client):
        r = api_client.post("/sumar", json={"dato": ""})
        assert r.status_code == 400

    def test_dato_solo_espacios_retorna_400(self, api_client):
        r = api_client.post("/sumar", json={"dato": "   "})
        assert r.status_code == 400

    def test_dato_con_letras_retorna_422(self, api_client):
        r = api_client.post("/sumar", json={"dato": "1+abc"})
        assert r.status_code == 422

    def test_campo_faltante_retorna_422(self, api_client):
        r = api_client.post("/sumar", json={})
        assert r.status_code == 422
