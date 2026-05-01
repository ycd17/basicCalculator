from playwright.sync_api import Page, expect


def _digitar(page: Page, expresion: str) -> None:
    """Hace clic en los botones que forman la expresión (ej: '12+3')."""
    for char in expresion:
        page.get_by_role("button", name=char, exact=True).click()


class TestDisplay:
    def test_digitos_aparecen_en_display(self, page: Page, frontend_url):
        page.goto(frontend_url)
        _digitar(page, "123")
        assert page.locator("#display").input_value() == "123"

    def test_operador_se_agrega_al_display(self, page: Page, frontend_url):
        page.goto(frontend_url)
        _digitar(page, "1+2")
        assert page.locator("#display").input_value() == "1+2"

    def test_numero_compuesto_en_display(self, page: Page, frontend_url):
        page.goto(frontend_url)
        _digitar(page, "112")
        assert page.locator("#display").input_value() == "112"


class TestSuma:
    def test_suma_simple_muestra_resultado(self, page: Page, frontend_url):
        page.goto(frontend_url)
        _digitar(page, "1+2")
        page.get_by_role("button", name="=", exact=True).click()
        expect(page.locator("#resultado.ok")).to_be_visible()
        assert page.locator("#resultado").inner_text() == "= 3"

    def test_suma_numero_compuesto(self, page: Page, frontend_url):
        page.goto(frontend_url)
        _digitar(page, "112+21")
        page.get_by_role("button", name="=", exact=True).click()
        expect(page.locator("#resultado.ok")).to_be_visible()
        assert page.locator("#resultado").inner_text() == "= 133"

    def test_suma_multiples_operandos(self, page: Page, frontend_url):
        page.goto(frontend_url)
        _digitar(page, "1+2+3+4+5")
        page.get_by_role("button", name="=", exact=True).click()
        expect(page.locator("#resultado.ok")).to_be_visible()
        assert page.locator("#resultado").inner_text() == "= 15"


class TestLimpiar:
    def test_boton_c_limpia_display(self, page: Page, frontend_url):
        page.goto(frontend_url)
        _digitar(page, "123")
        page.get_by_role("button", name="C", exact=True).click()
        assert page.locator("#display").input_value() == ""

    def test_boton_c_limpia_resultado(self, page: Page, frontend_url):
        page.goto(frontend_url)
        _digitar(page, "1+2")
        page.get_by_role("button", name="=", exact=True).click()
        expect(page.locator("#resultado.ok")).to_be_visible()
        page.get_by_role("button", name="C", exact=True).click()
        assert page.locator("#resultado").inner_text() == ""


class TestErrores:
    def test_igual_con_display_vacio_muestra_error(self, page: Page, frontend_url):
        page.goto(frontend_url)
        page.get_by_role("button", name="=", exact=True).click()
        expect(page.locator("#resultado.error")).to_be_visible()
        assert "Ingresa" in page.locator("#resultado").inner_text()
