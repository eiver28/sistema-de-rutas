
import heapq

class Estacion:
    def __init__(self, nombre, lineas):
        self.nombre = nombre
        self.lineas = set(lineas) # Conjunto de líneas que pasan por esta estación

    def __lt__(self, other):
        return self.nombre < other.nombre

    def __eq__(self, other):
        return self.nombre == other.nombre

    def __hash__(self):
        return hash(self.nombre)

class SistemaTransporte:
    def __init__(self):
        self.estaciones = {}
        self.conexiones = {} # {estacion_origen: {estacion_destino: {linea: tiempo}}}

    def agregar_estacion(self, nombre, lineas):
        if nombre not in self.estaciones:
            self.estacion = Estacion(nombre, lineas)
            self.estaciones[nombre] = self.estacion
            self.conexiones[nombre] = {}

    def agregar_conexion(self, origen, destino, linea, tiempo):
        if origen not in self.estaciones or destino not in self.estaciones:
            raise ValueError("Estación de origen o destino no existe.")
        
        # Conexión bidireccional
        if destino not in self.conexiones[origen]:
            self.conexiones[origen][destino] = {}
        self.conexiones[origen][destino][linea] = tiempo

        if origen not in self.conexiones[destino]:
            self.conexiones[destino][origen] = {}
        self.conexiones[destino][origen][linea] = tiempo

    def obtener_vecinos(self, estacion_actual):
        return self.conexiones.get(estacion_actual.nombre, {})

    def heuristica(self, estacion_actual, estacion_destino):
        # Heurística simple: distancia en número de estaciones o 0 si no hay información
        # Para un sistema real, se usaría distancia geográfica, etc.
        return 0 # Simplificado para este ejemplo

    def buscar_ruta_a_estrella(self, inicio_nombre, destino_nombre, reglas=None):
        if inicio_nombre not in self.estaciones or destino_nombre not in self.estaciones:
            return None, "Estación de inicio o destino no encontrada."

        inicio = self.estaciones[inicio_nombre]
        destino = self.estaciones[destino_nombre]

        cola_prioridad = [(0, inicio, [inicio_nombre], 0)] # (f_cost, estacion, camino, g_cost)
        costos_g = {estacion_nombre: float('inf') for estacion_nombre in self.estaciones}
        costos_g[inicio_nombre] = 0
        
        visitados = set()

        while cola_prioridad:
            f_cost, estacion_actual, camino_actual, g_cost_actual = heapq.heappop(cola_prioridad)

            if estacion_actual == destino:
                return camino_actual, "Ruta encontrada.", costos_g

            if estacion_actual in visitados:
                continue
            visitados.add(estacion_actual)

            for vecino_nombre, lineas_info in self.obtener_vecinos(estacion_actual).items():
                vecino = self.estaciones[vecino_nombre]
                
                for linea, tiempo_viaje in lineas_info.items():
                    costo_transbordo = 0
                    if len(camino_actual) > 1: # Si no es la primera conexión
                        ultima_estacion_camino = self.estaciones[camino_actual[-1]]
                        # Verificar si hay cambio de línea
                        lineas_comunes = estacion_actual.lineas.intersection(ultima_estacion_camino.lineas)
                        if not lineas_comunes or linea not in lineas_comunes: # Asumimos transbordo si no hay línea común o si la línea actual no es una de las comunes
                            costo_transbordo = 5 # Costo fijo por transbordo

                    nuevo_g_cost = g_cost_actual + tiempo_viaje + costo_transbordo

                    # Aplicar reglas lógicas
                    if reglas:
                        if 'evitar_linea' in reglas and linea == reglas['evitar_linea']:
                            continue # Saltar esta conexión si la línea debe ser evitada
                        if 'preferir_linea' in reglas and linea != reglas['preferir_linea'] and reglas['preferir_linea'] in estacion_actual.lineas and reglas['preferir_linea'] in vecino.lineas:
                            # Penalizar si no se usa la línea preferida cuando está disponible
                            nuevo_g_cost += 10 

                    if nuevo_g_cost < costos_g[vecino_nombre]:
                        costos_g[vecino_nombre] = nuevo_g_cost
                        f_cost = nuevo_g_cost + self.heuristica(vecino, destino)
                        heapq.heappush(cola_prioridad, (f_cost, vecino, camino_actual + [vecino_nombre], nuevo_g_cost))

        return None, "No se encontró una ruta.", None

# --- Ejemplo de Uso ---
if __name__ == "__main__":
    sistema = SistemaTransporte()

    # Agregar estaciones con sus líneas
    sistema.agregar_estacion("A", ["L1"])
    sistema.agregar_estacion("B", ["L1", "L2"])
    sistema.agregar_estacion("C", ["L1"])
    sistema.agregar_estacion("D", ["L2", "L3"])
    sistema.agregar_estacion("E", ["L3"])
    sistema.agregar_estacion("F", ["L1", "L3"])

    # Agregar conexiones (origen, destino, linea, tiempo)
    sistema.agregar_conexion("A", "B", "L1", 10)
    sistema.agregar_conexion("B", "C", "L1", 8)
    sistema.agregar_conexion("B", "D", "L2", 12)
    sistema.agregar_conexion("C", "F", "L1", 15)
    sistema.agregar_conexion("D", "E", "L3", 7)
    sistema.agregar_conexion("F", "E", "L3", 10)

    print("--- Búsqueda de Ruta Simple (A a E) ---")
    ruta, mensaje, costos_finales = sistema.buscar_ruta_a_estrella("A", "E")
    if ruta:
        print(f"Ruta: {' -> '.join(ruta)}")
        print(f"Costo total (aproximado): {costos_finales[ruta[-1]]}")
    else:
        print(mensaje)

    print("\n--- Búsqueda de Ruta Evitando Línea L2 (A a E) ---")
    reglas_evitar_L2 = {'evitar_linea': "L2"}
    ruta_evitar, mensaje_evitar, costos_evitar = sistema.buscar_ruta_a_estrella("A", "E", reglas_evitar_L2)
    if ruta_evitar:
        print(f"Ruta: {' -> '.join(ruta_evitar)}")
        print(f"Costo total (aproximado): {costos_evitar[ruta_evitar[-1]]}")
    else:
        print(mensaje_evitar)

    print("\n--- Búsqueda de Ruta Prefiriendo Línea L3 (A a E) ---")
    reglas_preferir_L3 = {'preferir_linea': "L3"}
    ruta_preferir, mensaje_preferir, costos_preferir = sistema.buscar_ruta_a_estrella("A", "E", reglas_preferir_L3)
    if ruta_preferir:
        print(f"Ruta: {' -> '.join(ruta_preferir)}")
        print(f"Costo total (aproximado): {costos_preferir[ruta_preferir[-1]]}")
    else:
        print(mensaje_preferir)

