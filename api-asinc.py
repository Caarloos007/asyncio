import asyncio
import aiohttp
import time

# 1. Definimos las APIs que vamos a consultar (mínimo 5)
APIS_A_CONSULTAR = [
    {"nombre": "Chuck Norris", "url": "https://api.chucknorris.io/jokes/random", "headers": {}},
    {"nombre": "Dato de Gato", "url": "https://catfact.ninja/fact", "headers": {}},
    {"nombre": "Chiste Corto", "url": "https://icanhazdadjoke.com/", "headers": {"Accept": "application/json"}},
    {"nombre": "Foto de Perro", "url": "https://dog.ceo/api/breeds/image/random", "headers": {}},
    {"nombre": "Predicción Edad", "url": "https://api.agify.io?name=fausto", "headers": {}}
]

# 2. Función asíncrona para hacer UNA petición
async def consultar_api(session, api_info):
    nombre = api_info["nombre"]
    url = api_info["url"]
    headers = api_info.get("headers", {})
    
    # Manejo de tiempos de espera: máximo 5 segundos por petición
    timeout = aiohttp.ClientTimeout(total=5)

    try:
        # Hacemos la petición GET
        async with session.get(url, headers=headers, timeout=timeout) as response:
            response.raise_for_status() # Comprueba si hay errores HTTP (404, 500...)
            data = await response.json()

            # Extraemos la información relevante según la API
            resultado = ""
            if nombre == "Chuck Norris":
                resultado = data.get("value")
            elif nombre == "Dato de Gato":
                resultado = data.get("fact")
            elif nombre == "Chiste Corto":
                resultado = data.get("joke")
            elif nombre == "Foto de Perro":
                resultado = f"URL de la imagen: {data.get('message')}"
            elif nombre == "Predicción Edad":
                resultado = f"A la gente llamada {data.get('name').capitalize()} se le estima una edad de {data.get('age')} años."

            return {"nombre": nombre, "estado": "OK", "datos": resultado}

    # 3. Manejo de errores
    except asyncio.TimeoutError:
        return {"nombre": nombre, "estado": "ERROR", "datos": "Tiempo de espera agotado (Timeout)."}
    except aiohttp.ClientError as e:
        return {"nombre": nombre, "estado": "ERROR", "datos": f"Error de conexión: {e}"}
    except Exception as e:
        return {"nombre": nombre, "estado": "ERROR", "datos": f"Error inesperado: {e}"}

# 4. Función principal que lanza todo
async def main():
    print("Iniciando recolección de datos asíncrona...\n")
    inicio = time.perf_counter()

    # Creamos una única sesión para todas las peticiones (buena práctica)
    async with aiohttp.ClientSession() as session:
        # Preparamos las tareas
        tareas = [consultar_api(session, api) for api in APIS_A_CONSULTAR]
        
        # Lanzamos todas las peticiones CONCURRENTEMENTE
        resultados = await asyncio.gather(*tareas)

    fin = time.perf_counter()

    # 5. Presentación original y legible
    print("=" * 60)
    print(" RESULTADOS DEL DASHBOARD MULTI-API ")
    print("=" * 60)

    for res in resultados:
        if res["estado"] == "OK":
            print(f"[OK] [{res['nombre']}]:\n   {res['datos']}\n")
        else:
            print(f"[ERROR] [{res['nombre']}] FALLÓ:\n   {res['datos']}\n")

    print("=" * 60)
    print(f"Tiempo total de ejecución: {fin - inicio:.2f} segundos")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())