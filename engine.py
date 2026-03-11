# engine.py
from config_disc import DISC_MAP

def calcular_resultados_disc(respuestas_usuario):
    # Tomaremos una lista de 24 respuestas y calcularemos los procentajes de D, I, S y C.
    # La entrada serán ['A', 'B', 'C', 'D', ...] con 24 elementos.
    # Y la salida serán un diccionarios de porcentajes para cada dimensión DISC.

    # 1. Inicializamos un contador para cada dimensión
    conteo_disc = {'D': 0, 'I': 0, 'S': 0, 'C':0}
    total_preguntas = len(respuestas_usuario)

    # 2. Iteramos sobre las respuestas del usuario y contamos las dimensiones correspondientes
    for i, respuesta in enumerate(respuestas_usuario, 1):

        # Buscamos en nuestro diccionario DISC_MAP la dimensión correspondiente para la pregunta i
        dimensión = DISC_MAP[i][respuesta]

        #Sumamos 1 al contador de esa dimensión
        conteo_disc[dimensión] += 1

    # 3. Calculamos los porcentajes para cada dimensión (Decimales para SQL)
    # Aplicamos la formula (Conteo de la dimensión / Total de preguntas)
    resultados_finales = {
        dim: round(valor/total_preguntas, 2)
        for dim, valor in conteo_disc.items()
    }

    return resultados_finales

