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
| Pruebas Capa 3 — E2E Playwright | ⏳ Pendiente |

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
│   └── test_capa3_e2e.py       # Por crear — pruebas Playwright
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
pytest                              # todas las capas
pytest tests/test_capa1_backend.py  # solo capa 1 (no necesita servidor)
pytest tests/test_capa2_api.py      # solo capa 2 (no necesita servidor, usa TestClient)
```

> La Capa 1 y la Capa 2 no necesitan un servidor corriendo — usan la función y el `TestClient` directamente.
> La Capa 3 (Playwright) levanta el servidor automáticamente en el puerto **8001** para no chocar con el servidor de desarrollo en 8000.

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
dato vacío o solo espacios  →  400 Bad Request      (no hay contenido que procesar)
dato con caracteres inválidos →  422 Unprocessable Entity  (hay contenido, pero no se puede procesar)
campo 'dato' ausente en JSON  →  422 Unprocessable Entity  (FastAPI/Pydantic, nunca llega al backend)
```

Esta distinción está implementada en `backend/main.py`:
```python
status = 400 if not req.dato.strip() else 422
```

---

### Capa 3 — E2E Playwright `test_capa3_e2e.py`

Prueba el flujo completo en Chromium: clic en botones → display → llamada API → resultado visible. Debe cubrir:
- Dígitos y operador aparecen en el display
- `=` muestra el resultado correcto
- `C` limpia display y resultado
- `=` con display vacío muestra error

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
