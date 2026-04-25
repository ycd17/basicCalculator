def sumar(dato: str) -> int:
    return sum(int(n) for n in dato.split("+") if n.strip())
