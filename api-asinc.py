import asyncio
import aiohttp
import time

# ─────────────────────────────────────────────
#  Paleta de colores ANSI para la consola
# ─────────────────────────────────────────────
class Color:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    GREEN   = "\033[92m"
    RED     = "\033[91m"
    CYAN    = "\033[96m"
    YELLOW  = "\033[93m"
    MAGENTA = "\033[95m"
    BLUE    = "\033[94m"
    GREY    = "\033[90m"

# ─────────────────────────────────────────────
#  APIs a consultar  (todas las del enunciado)
# ─────────────────────────────────────────────
APIS = [
    {
        "nombre":  "🥊 Chuck Norris",
        "emoji":   "🥊",
        "url":     "https://api.chucknorris.io/jokes/random",
        "headers": {},
    },
    {
        "nombre":  "🐱 Dato de Gato",
        "emoji":   "🐱",
        "url":     "https://catfact.ninja/fact",
        "headers": {},
    },
    {
        "nombre":  "😂 Chiste Corto",
        "emoji":   "😂",
        "url":     "https://icanhazdadjoke.com/",
        "headers": {"Accept": "application/json"},
    },
    {
        "nombre":  "🐶 Foto de Perro",
        "emoji":   "🐶",
        "url":     "https://dog.ceo/api/breeds/image/random",
        "headers": {},
    },
    {
        "nombre":  "🎂 Predicción Edad",
        "emoji":   "🎂",
        "url":     "https://api.agify.io?name=fausto",
        "headers": {},
    },
    {
        "nombre":  "🎭 Chiste Oficial",
        "emoji":   "🎭",
        "url":     "https://official-joke-api.appspot.com/random_joke",
        "headers": {},
    },
    {
        "nombre":  "🌤️  Clima Berlín",
        "emoji":   "🌤️",
        "url":     "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current_weather=true",
        "headers": {},
    },
    {
        "nombre":  "👤 Usuario Aleatorio",
        "emoji":   "👤",
        "url":     "https://randomuser.me/api/",
        "headers": {},
    },
]

# ─────────────────────────────────────────────
#  Extracción de datos por API
# ─────────────────────────────────────────────
def extraer_dato(nombre: str, data: dict) -> str:
    if "Chuck Norris"      in nombre: return data.get("value", "")
    if "Gato"              in nombre: return data.get("fact", "")
    if "Chiste Corto"      in nombre: return data.get("joke", "")
    if "Foto de Perro"     in nombre: return f"🔗 {data.get('message', '')}"
    if "Predicción Edad"   in nombre:
        return (f"El nombre '{data.get('name','').capitalize()}' "
                f"tiene una edad estimada de {data.get('age')} años.")
    if "Chiste Oficial"    in nombre:
        return f"{data.get('setup','')} — {data.get('punchline','')}"
    if "Clima"             in nombre:
        w = data.get("current_weather", {})
        return f"Temperatura: {w.get('temperature')}°C | Viento: {w.get('windspeed')} km/h"
    if "Usuario"           in nombre:
        u = data.get("results", [{}])[0]
        n = u.get("name", {})
        loc = u.get("location", {})
        return (f"{n.get('first','')} {n.get('last','')} "
                f"— {loc.get('city','')}, {loc.get('country','')}")
    return str(data)

# ─────────────────────────────────────────────
#  Petición individual con medición de tiempo
# ─────────────────────────────────────────────
async def consultar_api(session: aiohttp.ClientSession, api: dict) -> dict:
    nombre  = api["nombre"]
    url     = api["url"]
    headers = api.get("headers", {})
    timeout = aiohttp.ClientTimeout(total=5)
    t0      = time.perf_counter()

    try:
        async with session.get(url, headers=headers, timeout=timeout) as resp:
            resp.raise_for_status()
            data    = await resp.json(content_type=None)  # tolera content-type raro
            elapsed = time.perf_counter() - t0
            return {
                "nombre":  nombre,
                "estado":  "OK",
                "datos":   extraer_dato(nombre, data),
                "tiempo":  elapsed,
            }

    except asyncio.TimeoutError:
        return {"nombre": nombre, "estado": "TIMEOUT",
                "datos": "Tiempo de espera agotado.", "tiempo": 5.0}
    except aiohttp.ClientResponseError as e:
        return {"nombre": nombre, "estado": "HTTP_ERR",
                "datos": f"Código {e.status}: {e.message}", "tiempo": time.perf_counter() - t0}
    except Exception as e:
        return {"nombre": nombre, "estado": "ERROR",
                "datos": str(e), "tiempo": time.perf_counter() - t0}

# ─────────────────────────────────────────────
#  Barra de tiempo visual  (max 5 s → 20 bloques)
# ─────────────────────────────────────────────
def barra_tiempo(segundos: float, maximo: float = 5.0, largo: int = 20) -> str:
    llenos = int(min(segundos / maximo, 1.0) * largo)
    color  = Color.GREEN if segundos < 1.5 else Color.YELLOW if segundos < 3 else Color.RED
    barra  = "█" * llenos + "░" * (largo - llenos)
    return f"{color}{barra}{Color.RESET} {segundos:.2f}s"

# ─────────────────────────────────────────────
#  Presentación de resultados
# ─────────────────────────────────────────────
def imprimir_resultados(resultados: list, tiempo_total: float):
    ancho = 64

    print(f"\n{Color.BOLD}{Color.CYAN}{'═' * ancho}{Color.RESET}")
    titulo = "  🌐  DASHBOARD MULTI-API ASÍNCRONO  🌐"
    print(f"{Color.BOLD}{Color.CYAN}{titulo.center(ancho)}{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}{'═' * ancho}{Color.RESET}\n")

    ok_count  = sum(1 for r in resultados if r["estado"] == "OK")
    err_count = len(resultados) - ok_count

    for res in resultados:
        nombre = res["nombre"]
        estado = res["estado"]
        datos  = res["datos"]
        tiempo = res["tiempo"]

        if estado == "OK":
            icono  = f"{Color.GREEN}✔{Color.RESET}"
            header = f"{Color.BOLD}{Color.GREEN}{nombre}{Color.RESET}"
        else:
            icono  = f"{Color.RED}✘{Color.RESET}"
            etiq   = {"TIMEOUT": "⏱ TIMEOUT", "HTTP_ERR": "🔴 HTTP ERR"}.get(estado, "💥 ERROR")
            header = f"{Color.BOLD}{Color.RED}{nombre}  [{etiq}]{Color.RESET}"

        print(f"  {icono}  {header}")
        print(f"     {Color.GREY}{'─' * (ancho - 6)}{Color.RESET}")

        print(f"     {Color.YELLOW}{datos}{Color.RESET}")

        # Barra de tiempo
        print(f"     ⏱  {barra_tiempo(tiempo)}")
        print()

    # ── Resumen final ──────────────────────────────────────────────
    print(f"{Color.CYAN}{'─' * ancho}{Color.RESET}")
    print(f"  {Color.BOLD}Peticiones exitosas : {Color.GREEN}{ok_count}/{len(resultados)}{Color.RESET}")
    if err_count:
        print(f"  {Color.BOLD}Con errores         : {Color.RED}{err_count}{Color.RESET}")
    print(f"  {Color.BOLD}Tiempo TOTAL        : {Color.MAGENTA}{tiempo_total:.2f}s{Color.RESET}  "
          f"{Color.GREY}(si fuera secuencial: ~{sum(r['tiempo'] for r in resultados):.1f}s){Color.RESET}")
    print(f"{Color.CYAN}{'═' * ancho}{Color.RESET}\n")

# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────
async def main():
    print(f"\n{Color.GREY}Lanzando {len(APIS)} peticiones concurrentes...{Color.RESET}")
    t0 = time.perf_counter()

    async with aiohttp.ClientSession() as session:
        tareas      = [consultar_api(session, api) for api in APIS]
        resultados  = await asyncio.gather(*tareas)

    tiempo_total = time.perf_counter() - t0
    imprimir_resultados(list(resultados), tiempo_total)

if __name__ == "__main__":
    asyncio.run(main())
