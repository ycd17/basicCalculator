import pytest


# ---------------------------------------------------------------------------
# A-01: Health-check
# ---------------------------------------------------------------------------

class TestSalud:

    def test_A_01_01_health_check(self, cliente_api):
        r = cliente_api.get("/salud")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# A-02: Sumas válidas → 200 OK
# ---------------------------------------------------------------------------

class TestSumasValidas:

    def test_A_02_01_suma_simple(self, cliente_api):
        r = cliente_api.post("/sumar", json={"dato": "3 + 5"})
        assert r.status_code == 200
        assert r.json()["resultado"] == 8.0

    def test_A_02_02_resultado_es_float(self, cliente_api):
        r = cliente_api.post("/sumar", json={"dato": "10 + 20"})
        assert r.status_code == 200
        assert isinstance(r.json()["resultado"], float)

    def test_A_02_03_decimales(self, cliente_api):
        r = cliente_api.post("/sumar", json={"dato": "1.5 + 2.5"})
        assert r.status_code == 200
        assert r.json()["resultado"] == pytest.approx(4.0)

    def test_A_02_04_un_solo_numero(self, cliente_api):
        r = cliente_api.post("/sumar", json={"dato": "42"})
        assert r.status_code == 200
        assert r.json()["resultado"] == 42.0

    def test_A_02_05_content_type_json(self, cliente_api):
        r = cliente_api.post("/sumar", json={"dato": "1 + 1"})
        assert r.status_code == 200
        assert "application/json" in r.headers["content-type"]


# ---------------------------------------------------------------------------
# A-03: Expresión llega al backend pero es inválida
#
# Nota de diseño (ver main.py línea 24):
#   status = 400 si dato.strip() está vacío, 422 en cualquier otro caso inválido.
# Por eso la expresión vacía devuelve 400, y el resto devuelve 422.
# ---------------------------------------------------------------------------

class TestExpresionesInvalidas:

    def test_A_03_01_expresion_vacia_retorna_400(self, cliente_api):
        r = cliente_api.post("/sumar", json={"dato": ""})
        assert r.status_code == 400

    def test_A_03_02_operador_invalido_retorna_422(self, cliente_api):
        r = cliente_api.post("/sumar", json={"dato": "3 * 5"})
        assert r.status_code == 422

    def test_A_03_03_letras_retorna_422(self, cliente_api):
        r = cliente_api.post("/sumar", json={"dato": "tres + cinco"})
        assert r.status_code == 422

    def test_A_03_04_respuesta_incluye_detail(self, cliente_api):
        r = cliente_api.post("/sumar", json={"dato": "3 * 5"})
        body = r.json()
        assert "detail" in body
        assert body["detail"]


# ---------------------------------------------------------------------------
# A-04: FastAPI rechaza el request antes de llegar al backend → 422
# ---------------------------------------------------------------------------

class TestCamposInvalidos:

    def test_A_04_01_sin_campo_dato(self, cliente_api):
        r = cliente_api.post("/sumar", json={})
        assert r.status_code == 422

    def test_A_04_02_campo_mal_nombrado(self, cliente_api):
        r = cliente_api.post("/sumar", json={"expression": "3+5"})
        assert r.status_code == 422

    def test_A_04_03_body_vacio(self, cliente_api):
        r = cliente_api.post("/sumar")
        assert r.status_code == 422

    def test_A_04_04_dato_numerico_nunca_500(self, cliente_api):
        r = cliente_api.post("/sumar", json={"dato": 12345})
        assert r.status_code != 500


# ---------------------------------------------------------------------------
# A-05: Paramétricos — válidos e inválidos
# ---------------------------------------------------------------------------

class TestParametricos:

    @pytest.mark.parametrize("dato, esperado", [
        ("0 + 0",            0.0),
        ("10 + 20",         30.0),
        ("100 + 200 + 300", 600.0),
        ("0.5 + 0.5",         1.0),
    ])
    def test_A_05_validos(self, cliente_api, dato, esperado):
        r = cliente_api.post("/sumar", json={"dato": dato})
        assert r.status_code == 200
        assert r.json()["resultado"] == pytest.approx(esperado)

    @pytest.mark.parametrize("dato", [
        "",
        "abc",
        "3 * 5",
        "1 ++ 2",
        "+ 3 + 5",
    ])
    def test_A_05_invalidos_nunca_500(self, cliente_api, dato):
        r = cliente_api.post("/sumar", json={"dato": dato})
        assert r.status_code != 200
        assert r.status_code != 500


# ---------------------------------------------------------------------------
# A-EX: Casos de extensión
# ---------------------------------------------------------------------------

class TestExtras:

    def test_A_EX_01_dato_null(self, cliente_api):
        # Pydantic v2 rechaza None en un campo str → 422 (nunca llega al backend)
        r = cliente_api.post("/sumar", json={"dato": None})
        assert r.status_code != 500

    def test_A_EX_02_campo_extra_ignorado(self, cliente_api):
        # FastAPI ignora campos desconocidos en el body → 200 normal
        r = cliente_api.post("/sumar", json={"dato": "1 + 1", "campo_extra": "ignorado"})
        assert r.status_code == 200
        assert r.json()["resultado"] == pytest.approx(2.0)
