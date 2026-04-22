import asyncio
import aiohttp
import time

# 1. Definimos las APIs públicas a consultar
APIS_A_CONSULTAR = [
    {"nombre": "Chuck Norris", "url": "https://api.chucknorris.io/jokes/random", "headers": {}},
    {"nombre": "Dato de Gato", "url": "https://catfact.ninja/fact", "headers": {}},
    {"nombre": "Chiste Corto", "url": "https://icanhazdadjoke.com/", "headers": {"Accept": "application/json"}},
    {"nombre": "Foto de Perro", "url": "https://dog.ceo/api/breeds/image/random", "headers": {}},
    {"nombre": "Predicción Edad", "url": "https://api.agify.io?name=fausto", "headers": {}},
    {"nombre": "Usuario Aleatorio", "url": "https://randomuser.me/api/", "headers": {}},
    {"nombre": "Post de JSONPlaceholder", "url": "https://jsonplaceholder.typicode.com/posts/1", "headers": {}},
    {"nombre": "Clima Actual", "url": "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current_weather=true", "headers": {}},
]

# 2. Función asíncrona para hacer cada petición individualmente
async def consultar_api(session, api_info):
    nombre = api_info["nombre"]
    url = api_info["url"]
    headers = api_info.get("headers", {})
    
    # Manejo de tiempos de espera: máximo 5 segundos por petición
    timeout = aiohttp.ClientTimeout(total=5)

    try:
        # Petición GET asíncrona
        async with session.get(url, headers=headers, timeout=timeout) as response:
            response.raise_for_status() # Lanza error si el código HTTP no es 200 OK
            data = await response.json()

            # Extracción limpia de la información según la API
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
            elif nombre == "Usuario Aleatorio":
                user = data.get("results", [{}])[0]
                name = user.get("name", {})
                resultado = f"Usuario: {name.get('first', '')} {name.get('last', '')}"
            elif nombre == "Post de JSONPlaceholder":
                resultado = data.get("title", "")
            elif nombre == "Clima Actual":
                weather = data.get("current_weather", {})
                resultado = f"Temperatura: {weather.get('temperature', '')}°C"
            elif nombre == "Frase Inspiracional":
                resultado = data.get("content", "")
            elif nombre == "Número Aleatorio":
                resultado = data.get("text", "")

            return {"nombre": nombre, "estado": "OK", "datos": resultado}

    # 3. Manejo de errores de red o timeouts
    except asyncio.TimeoutError:
        return {"nombre": nombre, "estado": "ERROR", "datos": "Tiempo de espera agotado (Timeout)."}
    except aiohttp.ClientError as e:
        return {"nombre": nombre, "estado": "ERROR", "datos": f"Error de conexión: {e}"}
    except Exception as e:
        return {"nombre": nombre, "estado": "ERROR", "datos": f"Error inesperado: {e}"}

# 4. Función principal que orquesta la concurrencia
async def main():
    inicio = time.perf_counter()

    # Se usa una única sesión HTTP para mejorar el rendimiento
    async with aiohttp.ClientSession() as session:
        # Preparamos la lista de tareas a ejecutar (2 peticiones por API)
        tareas = []
        for api in APIS_A_CONSULTAR:
            for _ in range(2):
                tareas.append(consultar_api(session, api))
        
        # Lanzamos las peticiones de forma CONCURRENTE
        resultados = await asyncio.gather(*tareas)

    fin = time.perf_counter()

    # 5. Imprimir resultados con la presentación requerida
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

if __name__ == "__main__":
    # Inicia el bucle de eventos (event loop)
    asyncio.run(main())