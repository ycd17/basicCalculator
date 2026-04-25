# Calculadora 1-2

Aplicación de tres capas que permite construir expresiones de suma con los dígitos del `0` al `9`, evalúa la expresión a través de una API Python y muestra el resultado en el navegador.

## Arquitectura

```
frontend/
└── index.html          # Interfaz de usuario (HTML + CSS + JS vanilla)

backend/
├── main.py             # API FastAPI — capa de transporte HTTP
├── services/
│   └── calculator.py   # Lógica de negocio — parseo y suma
└── requirements.txt
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

## Levantar el backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

La API queda disponible en `http://localhost:8000`.

Documentación interactiva (Swagger): `http://localhost:8000/docs`

## Levantar el frontend

Abrir `frontend/index.html` directamente en el navegador:

```bash
# Opción A — doble clic en el archivo
# Opción B — desde terminal
start frontend/index.html          # Windows
open  frontend/index.html          # macOS
xdg-open frontend/index.html       # Linux
```

> El frontend apunta a `http://localhost:8000` — asegúrate de que el backend esté corriendo antes de presionar `=`.

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

## Casos de error

| Situación | Respuesta |
|-----------|-----------|
| Campo vacío | `400 Bad Request` — "El campo dato no puede estar vacío" |
| Caracteres no numéricos | `422 Unprocessable Entity` — "Formato inválido…" |
| API no disponible | El frontend muestra "No se pudo conectar con la API" |
