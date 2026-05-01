# Calculadora 1-2

Aplicación de tres capas que permite construir expresiones de suma con los dígitos del `0` al `9`, evalúa la expresión a través de una API Python y muestra el resultado en el navegador.

## Arquitectura

```
frontend/
└── index.html              # Interfaz de usuario (HTML + CSS + JS vanilla)

backend/
├── main.py                 # API FastAPI — capa de transporte HTTP
├── services/
│   └── calculator.py       # Lógica de negocio — parseo y suma
└── requirements.txt

tests/
├── conftest.py             # Fixtures compartidos (servidor, cliente HTTP)
├── unit/
│   └── test_calculator.py  # Pruebas unitarias del servicio de suma
├── api/
│   └── test_api.py         # Pruebas de integración del endpoint HTTP
└── e2e/
    └── test_ui.py          # Pruebas end-to-end con Playwright
```

### Flujo de datos

```
[Usuario] → clic "=" → fetch POST /sumar {"dato":"112+21"}
                                  ↓
                        FastAPI valida el request
                                  ↓
                        calculator.sumar("112+21")
                                  ↓
                        {"resultado": 133}
                                  ↓
              [Navegador muestra "= 133"]
```

## Principios aplicados

| Principio | Aplicación |
|-----------|-----------|
| **SRP** | `calculator.py` solo hace la suma; `main.py` solo maneja HTTP |
| **OCP** | Agregar nuevas operaciones no requiere modificar el endpoint existente |
| **DI**  | El endpoint recibe el servicio como función pura, fácil de testear en aislamiento |
| **Economía de código** | `sumar` resuelve parseo + suma en una sola línea con una comprensión |

## Requisitos

- Python 3.9+
- Un navegador moderno (Chrome, Firefox, Edge)

## Levantar la aplicación

El backend sirve también el frontend — un solo comando levanta todo:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

| URL | Qué es |
|-----|--------|
| `http://localhost:8000/` | Calculadora (frontend) |
| `http://localhost:8000/sumar` | Endpoint de la API |
| `http://localhost:8000/docs` | Documentación interactiva (Swagger) |

## Cómo usar la aplicación

1. Presiona los botones **1** y **2** para ingresar dígitos (puedes formar números como `112`, `21`, `1`).
2. Presiona **+** para agregar un operador de suma.
3. Repite para agregar más operandos.
4. Presiona **=** para enviar la expresión a la API y ver el resultado.

**Ejemplo:** `112` → `+` → `21` → `+` → `2` → `=` → **= 135**

## Probar la API directamente

Con `curl`:

```bash
curl -X POST http://localhost:8000/sumar \
     -H "Content-Type: application/json" \
     -d '{"dato": "112+21+2"}'
# → {"resultado": 135}
```

Con Swagger: abre `http://localhost:8000/docs`, usa el endpoint `POST /sumar`.

## Pruebas automatizadas

### Instalación

```bash
pip install -r requirements-test.txt
playwright install chromium
```

### Ejecutar todas las pruebas

> Asegúrate de que el puerto **8000** esté libre antes de correr los tests.

```bash
pytest
```

### Ejecutar por capa

```bash
pytest tests/unit   # Unitarias — sin servidor ni navegador
pytest tests/api    # Integración — levanta API en :8000
pytest tests/e2e    # E2E — levanta servidor en :8000, abre Chromium
```

### Servidores que gestiona pytest automáticamente

| Puerto | Qué sirve | Fixture | Scope |
|--------|-----------|---------|-------|
| `8000` | API + frontend (mismo origen) | `backend_server` | sesión |

### Cobertura de pruebas

| Capa | Archivo | Qué verifica |
|------|---------|-------------|
| Unit | `test_calculator.py` | Parseo y suma correcta, errores con letras |
| API  | `test_api.py` | Respuestas HTTP 200 / 400 / 422 por escenario |
| E2E  | `test_ui.py` | Flujo completo en navegador: botones, resultado, limpiar, error |

## Casos de error

| Situación | Respuesta |
|-----------|-----------|
| Campo vacío | `400 Bad Request` — "El campo dato no puede estar vacío" |
| Caracteres no numéricos | `422 Unprocessable Entity` — "Formato inválido…" |
| API no disponible | El frontend muestra "No se pudo conectar con la API" |
