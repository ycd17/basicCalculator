import pytest


# ---------------------------------------------------------------------------
# Fixture: página limpia por cada test (scope='function' implícito)
# ---------------------------------------------------------------------------

@pytest.fixture
def pagina(playwright, frontend_url):
    browser = playwright.chromium.launch(headless=True)
    page    = browser.new_context().new_page()
    page.goto(frontend_url)
    yield page
    browser.close()


# ---------------------------------------------------------------------------
# Helpers reutilizables
# ---------------------------------------------------------------------------

def presionar(pagina, *botones):
    for testid in botones:
        pagina.click(f"[data-testid='{testid}']")

def leer_expresion(pagina): return pagina.input_value('#expresion')
def leer_resultado(pagina): return pagina.inner_text('#resultado')
def leer_error(pagina):     return pagina.inner_text('#mensaje-error')


def _esperar_resultado(pagina, contiene=''):
    """Espera hasta que #resultado tenga contenido (o contenga el texto dado)."""
    cond = (
        f"document.getElementById('resultado').textContent.includes('{contiene}')"
        if contiene else
        "document.getElementById('resultado').textContent !== ''"
    )
    pagina.wait_for_function(cond)


# ---------------------------------------------------------------------------
# E-01 — Estado inicial de la página
# ---------------------------------------------------------------------------

class TestEstadoInicial:

    def test_E_01_01_titulo_visible(self, pagina):
        assert pagina.inner_text('h1') == 'Calculadora'

    def test_E_01_02_expresion_vacia_al_inicio(self, pagina):
        assert leer_expresion(pagina) == ''

    def test_E_01_03_resultado_vacio_al_inicio(self, pagina):
        assert leer_resultado(pagina) == ''

    def test_E_01_04_botones_digitos_visibles(self, pagina):
        for i in range(10):
            assert pagina.locator(f"[data-testid='btn-{i}']").is_visible()

    def test_E_01_05_boton_mas_visible(self, pagina):
        assert pagina.locator("[data-testid='btn-mas']").is_visible()

    def test_E_01_06_boton_igual_visible(self, pagina):
        assert pagina.locator("[data-testid='btn-igual']").is_visible()


# ---------------------------------------------------------------------------
# E-02 — Interacción con botones (actualización del display)
# ---------------------------------------------------------------------------

class TestInteraccionBotones:

    def test_E_02_01_clic_numero_actualiza_expresion(self, pagina):
        presionar(pagina, 'btn-3')
        assert leer_expresion(pagina) == '3'

    def test_E_02_02_multiples_numeros_se_concatenan(self, pagina):
        presionar(pagina, 'btn-1', 'btn-2', 'btn-3')
        assert leer_expresion(pagina) == '123'

    def test_E_02_03_boton_mas_agrega_operador(self, pagina):
        presionar(pagina, 'btn-5', 'btn-mas')
        assert leer_expresion(pagina) == '5 + '

    def test_E_02_04_mas_no_aparece_si_expresion_vacia(self, pagina):
        presionar(pagina, 'btn-mas')
        assert leer_expresion(pagina) == ''

    def test_E_02_05_mas_no_se_duplica(self, pagina):
        presionar(pagina, 'btn-3', 'btn-mas', 'btn-mas')
        assert leer_expresion(pagina).count('+') == 1

    def test_E_02_06_c_borra_todo(self, pagina):
        presionar(pagina, 'btn-3', 'btn-mas', 'btn-5', 'btn-borrar')
        assert leer_expresion(pagina) == ''
        assert leer_resultado(pagina) == ''


# ---------------------------------------------------------------------------
# E-03 — Cálculo completo extremo a extremo
# ---------------------------------------------------------------------------

class TestCalculo:

    def test_E_03_01_flujo_3_mas_5_igual_8(self, pagina):
        presionar(pagina, 'btn-3', 'btn-mas', 'btn-5', 'btn-igual')
        _esperar_resultado(pagina, '8')
        assert leer_resultado(pagina) == '= 8'

    def test_E_03_02_flujo_10_mas_20_mas_30_igual_60(self, pagina):
        presionar(pagina, 'btn-1', 'btn-0', 'btn-mas',
                  'btn-2', 'btn-0', 'btn-mas',
                  'btn-3', 'btn-0', 'btn-igual')
        _esperar_resultado(pagina, '60')
        assert leer_resultado(pagina) == '= 60'

    def test_E_03_03_c_borra_resultado_previo(self, pagina):
        presionar(pagina, 'btn-3', 'btn-mas', 'btn-5', 'btn-igual')
        _esperar_resultado(pagina)
        presionar(pagina, 'btn-borrar')
        assert leer_resultado(pagina) == ''

    def test_E_03_04_segunda_operacion_reemplaza_resultado(self, pagina):
        presionar(pagina, 'btn-3', 'btn-mas', 'btn-5', 'btn-igual')
        _esperar_resultado(pagina, '8')
        presionar(pagina, 'btn-borrar')
        presionar(pagina, 'btn-2', 'btn-mas', 'btn-2', 'btn-igual')
        _esperar_resultado(pagina, '4')
        assert leer_resultado(pagina) == '= 4'


# ---------------------------------------------------------------------------
# E-04 — Manejo de errores
# ---------------------------------------------------------------------------

class TestErrores:

    def test_E_04_01_igual_sin_expresion_muestra_error(self, pagina):
        presionar(pagina, 'btn-igual')
        pagina.wait_for_function(
            "document.getElementById('mensaje-error').textContent !== ''"
        )
        assert leer_error(pagina) != ''

    def test_E_04_02_escribir_borra_el_error(self, pagina):
        presionar(pagina, 'btn-igual')
        pagina.wait_for_function(
            "document.getElementById('mensaje-error').textContent !== ''"
        )
        presionar(pagina, 'btn-5')
        assert leer_error(pagina) == ''

    def test_E_04_03_resultado_vacio_si_expresion_vacia(self, pagina):
        presionar(pagina, 'btn-igual')
        pagina.wait_for_function(
            "document.getElementById('mensaje-error').textContent !== ''"
        )
        assert leer_resultado(pagina) == ''


# ---------------------------------------------------------------------------
# E-EX — Casos extra (deben pasar con la implementación actual)
# ---------------------------------------------------------------------------

class TestCasosExtra:

    def test_E_EX_01_tres_digitos_sin_espacios(self, pagina):
        """Presionar 1, 0, 0 → expresión muestra '100', no '1 0 0'."""
        presionar(pagina, 'btn-1', 'btn-0', 'btn-0')
        assert leer_expresion(pagina) == '100'

    def test_E_EX_02_cero_mas_cero_igual_cero(self, pagina):
        """0 + 0 = → resultado '= 0', no vacío ni error."""
        presionar(pagina, 'btn-0', 'btn-mas', 'btn-0', 'btn-igual')
        _esperar_resultado(pagina, '0')
        assert leer_resultado(pagina) == '= 0'

    def test_E_EX_03_operar_limpiar_y_volver_a_operar(self, pagina):
        """5+3=8, C limpia todo, 2+2=4 funciona con normalidad."""
        presionar(pagina, 'btn-5', 'btn-mas', 'btn-3', 'btn-igual')
        _esperar_resultado(pagina, '8')

        presionar(pagina, 'btn-borrar')
        assert leer_expresion(pagina) == ''
        assert leer_resultado(pagina) == ''

        presionar(pagina, 'btn-2', 'btn-mas', 'btn-2', 'btn-igual')
        _esperar_resultado(pagina, '4')
        assert leer_resultado(pagina) == '= 4'
