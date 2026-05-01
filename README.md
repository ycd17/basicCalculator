# Calculadora — Proyecto de tres capas

Aplicación web de suma. El usuario construye expresiones con dígitos y `+`, las envía a una API Python, y ve el resultado en pantalla.

---

## Estado actual del proyecto

| Componente | Estado |
|------------|--------|
| Frontend (HTML + JS) | Completo |
| Backend API (FastAPI) | Completo |
| Pruebas Capa 1 — Unitarias | 33/33 passing |
| Pruebas Capa 2 — API HTTP | 25/25 passing |
| Pruebas Capa 3 — E2E Playwright | 22/22 passing |

---

## Estructura del proyecto

```
clase/
├── frontend/
│   └── index.html              # UI: botones 0-9, +, =, C — JS vanilla
│
├── backend/
│   ├── main.py                 # FastAPI: GET /salud, POST /sumar, sirve el frontend
│   ├── services/
│   │   └── calculator.py       # sumar(dato: str) -> float + ErrorExpresion
│   └── requirements.txt
│
├── tests/
│   ├── conftest.py             # Fixtures: backend_server (uvicorn :8001), api_client (httpx), cliente_api (TestClient)
│   ├── test_capa1_backend.py   # Pruebas unitarias de sumar()
│   ├── test_capa2_api.py       # Pruebas HTTP del endpoint con TestClient
│   └── test_capa3_e2e.py       # Pruebas E2E con Playwright (Chromium headless)
│
├── requirements-test.txt
├── pytest.ini
└── README.md
```

---

## Cómo levantar la aplicación

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

| URL | Qué abre |
|-----|----------|
| `http://localhost:8000/` | Calculadora |
| `http://localhost:8000/salud` | Health-check JSON |
| `http://localhost:8000/docs` | Swagger / OpenAPI |

---

## Cómo correr las pruebas

### Primera vez (instalar dependencias)

```bash
pip install -r requirements-test.txt
playwright install chromium
```

### Correr pruebas

```bash
pytest                               # todas las capas
pytest tests/test_capa1_backend.py   # solo capa 1 (no necesita servidor)
pytest tests/test_capa2_api.py       # solo capa 2 (no necesita servidor, usa TestClient)
pytest tests/test_capa3_e2e.py       # solo capa 3 (levanta servidor en :8001 automáticamente)
```

> La Capa 1 y la Capa 2 no necesitan un servidor corriendo — usan la función y el `TestClient` directamente.
> La Capa 3 (Playwright) levanta el servidor automáticamente en el puerto **8001** para no chocar con el servidor de desarrollo en 8000.

### Generar reporte HTML

```bash
pytest --html=reporte.html --self-contained-html
```

Genera un único archivo `reporte.html` en la raíz del proyecto con el resultado de las tres capas. Se puede abrir directamente en el navegador haciendo doble clic.

Para generar el reporte de una sola capa:

```bash
pytest tests/test_capa1_backend.py --html=reporte.html --self-contained-html
pytest tests/test_capa2_api.py     --html=reporte.html --self-contained-html
pytest tests/test_capa3_e2e.py     --html=reporte.html --self-contained-html
```

### Screenshots y videos (Capa 3)

`pytest-playwright` captura evidencia visual automáticamente durante los tests E2E. El comportamiento está configurado en `pytest.ini`:

| Modo | Comportamiento |
|------|----------------|
| `--screenshot=only-on-failure` | Pantallazo solo cuando un test falla *(por defecto)* |
| `--screenshot=on` | Pantallazo al final de cada test |
| `--video=retain-on-failure` | Video solo cuando un test falla *(por defecto)* |
| `--video=on` | Video de todos los tests |

Para capturar evidencia completa de toda la ejecución (por ejemplo, para entregar):

```bash
pytest tests/test_capa3_e2e.py --screenshot=on --video=on
```

Los archivos se guardan en `test-results/`, con una carpeta por test:

```
test-results/
└── TestCalculo-test-E-03-01-flujo-3-mas-5-igual-8-chromium/
    ├── test-finished.png   ← pantallazo
    └── video.webm          ← video del test
```

> Los flags pasados por línea de comandos sobreescriben lo configurado en `pytest.ini`.

---

## Fixtures disponibles en `conftest.py`

| Fixture | Tipo | Cuándo usarlo |
|---------|------|---------------|
| `cliente_api` | `TestClient` (sin servidor) | Capa 2 — pruebas HTTP rápidas, no necesita uvicorn |
| `backend_server` | uvicorn en `:8001` | Capa 3 — Playwright necesita un servidor real |
| `api_client` | `httpx.Client` contra `:8001` | Alternativa HTTP con servidor real |
| `frontend_url` | URL base `:8001` | Capa 3 — dirección del frontend para el browser |

---

## Detalle por capa de pruebas

### Capa 1 — Unitarias `test_capa1_backend.py`

Prueba `sumar()` directamente, sin HTTP ni navegador.

**Técnicas aplicadas:** partición de equivalencia · análisis de valor límite · paramétricos

| Grupo | IDs | Qué cubre |
|-------|-----|-----------|
| B-01 | 01–07 | Casos válidos: enteros, decimales, espacios, número único, cero |
| B-02 | 01–02 | Límite de 200 chars: justo en el borde (válido) y borde+1 (inválido) |
| B-03 | 01–11 | Inválidos: vacío, espacios, `++`, empieza/termina con `+`, `*`, `-`, letras, inyección, tipos `int` y `None` |
| B-04 | — | 5 casos válidos + 5 inválidos paramétricos |
| B-EX | 01–03 | `0.1+0.2 ≈ 0.3` (approx), número grande, decimal mal puesto (`3.`) |

---

### Capa 2 — API HTTP `test_capa2_api.py`

Prueba el endpoint `POST /sumar` enviando peticiones HTTP reales con `TestClient` de FastAPI. No requiere levantar un servidor externo.

**Técnicas aplicadas:** códigos de estado HTTP · validación de body y headers · paramétricos · casos de frontera del framework

| Grupo | IDs | Entrada | HTTP esperado |
|-------|-----|---------|---------------|
| A-01 | 01 | `GET /salud` | `200` |
| A-02 | 01–05 | Expresiones válidas | `200`, `resultado` es `float`, `Content-Type: application/json` |
| A-03 | 01–04 | Expresión inválida (llega al backend) | `400` si vacía · `422` si no vacía |
| A-04 | 01–04 | Body malformado (FastAPI lo rechaza antes del backend) | `422` · nunca `500` |
| A-05 | — | 4 válidos + 5 inválidos paramétricos | `200` · `4xx` · nunca `500` |
| A-EX | 01–02 | `dato: null` · campo extra en el body | nunca `500` · `200` (campo extra se ignora) |

**Decisión de diseño importante — 400 vs 422 desde el backend:**

```
dato vacío o solo espacios    →  400 Bad Request           (no hay contenido que procesar)
dato con caracteres inválidos →  422 Unprocessable Entity  (hay contenido, pero no se puede procesar)
campo 'dato' ausente en JSON  →  422 Unprocessable Entity  (FastAPI/Pydantic, nunca llega al backend)
```

Esta distinción está implementada en `backend/main.py`:
```python
status = 400 if not req.dato.strip() else 422
```

---

### Capa 3 — E2E Playwright `test_capa3_e2e.py`

Prueba el flujo completo en Chromium headless: clic en botones del navegador → actualización del display → llamada a la API real → resultado visible en pantalla.

**Técnicas aplicadas:** selectores `data-testid` · espera asíncrona con `wait_for_function` · fixtures de sesión (servidor) y función (página limpia)

#### Cómo funciona internamente

El fixture `backend_server` (scope `session`) arranca uvicorn en `:8001` una sola vez para toda la sesión. El fixture `pagina` envuelve el `page` nativo de `pytest-playwright`, que abre un Chromium headless nuevo por test, navega a `http://127.0.0.1:8001/` y lo cierra al terminar, garantizando estado limpio. Al usar el `page` del plugin, Playwright puede capturar screenshots y videos automáticamente según la configuración de `pytest.ini`.

```
Test                     →  Playwright  →  Chromium  →  fetch POST /sumar  →  uvicorn :8001  →  sumar()
```

#### Selectores utilizados

Los botones del HTML tienen atributos `data-testid` que los tests usan para hacer clic de forma robusta, independiente del texto visual o del CSS:

| `data-testid` | Botón | Acción en el frontend |
|---|---|---|
| `btn-0` … `btn-9` | Dígitos 0–9 | Agrega el dígito a `#expresion` |
| `btn-mas` | `+` | Agrega ` + ` si la expresión no está vacía ni termina en `+` |
| `btn-igual` | `=` | Llama a la API y muestra resultado en `#resultado` |
| `btn-borrar` | `C` | Limpia `#expresion`, `#resultado` y `#mensaje-error` |

#### IDs del DOM leídos por los tests

| ID | Elemento | Qué contiene |
|----|----------|--------------|
| `#expresion` | `<input readonly>` | Expresión construida por el usuario |
| `#resultado` | `<div>` | Resultado del cálculo en formato `= X` |
| `#mensaje-error` | `<p>` | Mensaje de error cuando la operación falla |

#### Helpers reutilizables

```python
def presionar(pagina, *botones):          # hace clic en uno o varios data-testid
def leer_expresion(pagina) -> str:        # input_value('#expresion')
def leer_resultado(pagina) -> str:        # inner_text('#resultado')
def leer_error(pagina)     -> str:        # inner_text('#mensaje-error')
```

#### Mapa de casos de prueba

| ID | Descripción | Acciones | Resultado esperado |
|----|-------------|----------|--------------------|
| E-01-01 | Título visible | Cargar página | `h1` = `'Calculadora'` |
| E-01-02 | Expresión vacía al inicio | Cargar página | `#expresion` = `''` |
| E-01-03 | Resultado vacío al inicio | Cargar página | `#resultado` = `''` |
| E-01-04 | Botones 0–9 visibles | Cargar página | 10 botones `is_visible()` |
| E-01-05 | Botón + visible | Cargar página | `btn-mas` visible |
| E-01-06 | Botón = visible | Cargar página | `btn-igual` visible |
| E-02-01 | Clic en número actualiza expresión | Clic en `3` | `#expresion` = `'3'` |
| E-02-02 | Múltiples números se concatenan | Clic en `1`,`2`,`3` | `#expresion` = `'123'` |
| E-02-03 | Botón + agrega operador | Clic en `5`, `+` | `#expresion` = `'5 + '` |
| E-02-04 | + no aparece si expresión está vacía | Solo clic en `+` | `#expresion` = `''` |
| E-02-05 | + no se duplica | Clic en `3`, `+`, `+` | `#expresion` tiene solo 1 `+` |
| E-02-06 | C borra todo | Clic en `3`,`+`,`5`, luego `C` | `#expresion`=`''` y `#resultado`=`''` |
| E-03-01 | Flujo completo 3+5=8 | Clic: `3`,`+`,`5`,`=` | `#resultado` = `'= 8'` |
| E-03-02 | Flujo completo 10+20+30=60 | Clic: `1`,`0`,`+`,`2`,`0`,`+`,`3`,`0`,`=` | `#resultado` = `'= 60'` |
| E-03-03 | C borra resultado previo | Operar, luego `C` | `#resultado` = `''` |
| E-03-04 | Segunda operación reemplaza resultado | Dos operaciones con `C` entre ellas | `#resultado` = segunda |
| E-04-01 | = sin expresión muestra error | Solo clic en `=` | `#mensaje-error` ≠ `''` |
| E-04-02 | Escribir borra el error | Clic `=`, luego clic `5` | `#mensaje-error` = `''` |
| E-04-03 | Resultado vacío si expresión vacía | Solo clic en `=` | `#resultado` = `''` |
| E-EX-01 | Tres dígitos sin espacios | Clic `1`,`0`,`0` | `#expresion` = `'100'` |
| E-EX-02 | 0 + 0 = 0 | Clic `0`,`+`,`0`,`=` | `#resultado` = `'= 0'` |
| E-EX-03 | Operar, limpiar y volver a operar | `5+3=`, `C`, `2+2=` | expresión y resultado limpios entre operaciones, `#resultado` = `'= 4'` |

---

## Lógica de `sumar()` — `backend/services/calculator.py`

```
sumar(dato: str) -> float
  ├─ Valida que sea str                              → ErrorExpresion si no
  ├─ Valida longitud ≤ 200                           → ErrorExpresion si supera
  ├─ Valida no vacío                                 → ErrorExpresion si vacío
  ├─ Valida solo dígitos, +, . y espacios            → ErrorExpresion si no
  ├─ Valida no empieza/termina con +                 → ErrorExpresion si sí
  └─ Valida formato de cada número (^\d+(\.\d+)?$)   → ErrorExpresion si falla
```

**No usa `eval()`** — divide por `+` y convierte cada parte a `float`, evitando ejecución de código arbitrario.

---

## Comportamiento HTTP del endpoint

| Situación | Status |
|-----------|--------|
| `GET /salud` | `200 OK` + `{"estado": "ok"}` |
| Expresión válida | `200 OK` + `{"resultado": float}` |
| Expresión vacía o solo espacios | `400 Bad Request` |
| Caracteres no permitidos, formato inválido, longitud > 200 | `422 Unprocessable Entity` |
| Campo `dato` ausente, mal nombrado, o body vacío | `422 Unprocessable Entity` |
| Cualquier situación bien manejada | nunca `500 Internal Server Error` |
