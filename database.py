#database.py

import psycopg2
import streamlit as st

def obtener_conexion():
    try:
        # Establecemos la conexión enre VSCode y pgAdmin 4. 
        db_conf = st.secrets["postgres"]

        conn = psycopg2.connect(
            host=db_conf["host"],
            port=db_conf["port"],
            database=db_conf["database"],
            user=db_conf["user"],
            password=db_conf["password"]
        )
        return conn
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None


def obtener_password_test():
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT valor FROM configuracion WHERE clave = 'password_diaria'")
        res = cur.fetchone()
        cur.close()
        conn.close()
        return res[0] if res else None
    except:
        return None


def guardar_resultado_test(usuario_id, test_id, resultados_dict, envio_id):
    conn = obtener_conexion()
    if not conn:
        print("No se pudo establecer la conexión")
        return False
    
    cur = conn.cursor()

    try:
        # YA NO HACEMOS INSERT EN 'envios' AQUÍ. 
        # Usamos el envio_id que recibimos como parámetro desde app.py.

        # Insertamos los resultados de cada dimensión vinculados al ID oficial
        for dimension, puntaje in resultados_dict.items():
            cur.execute(
                "INSERT INTO resultados (envio_id, dimension, puntaje) VALUES (%s, %s, %s);",
                (envio_id, dimension, puntaje)
            )

        # Guardamos los cambios permanentemente
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"Resultados vinculados correctamente al Envío ID: {envio_id}")
        return True
    
    except Exception as e:
        if conn:
            conn.rollback()  # Revertimos cambios si algo falla
        print(f"Error al guardar resultados: {e}")
        return False
    

def obtener_o_crear_empresa(nombre_empresa):
    """Busca una empresa por nombre o la crea si no existe."""
    conn = obtener_conexion()
    if not conn: return None
    cur = conn.cursor()
    try:
        nombre_empresa = nombre_empresa.strip()
        # Buscamos ignorando mayúsculas/minúsculas para evitar duplicados
        cur.execute("SELECT id FROM empresas WHERE UPPER(nombre) = UPPER(%s);", (nombre_empresa,))
        resultado = cur.fetchone()
        
        if resultado:
            return resultado[0]
        else:
            # Si no existe, la creamos
            cur.execute("INSERT INTO empresas (nombre) VALUES (%s) RETURNING id;", (nombre_empresa,))
            emp_id = cur.fetchone()[0]
            conn.commit()
            return emp_id
    except Exception as e:
        print(f"Error al gestionar empresa: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def obtener_resultados_por_envio(envio_id):
    """ Busca en SQL los resultados reales de un test específico."""
    conn = obtener_conexion()
    if not conn:
        return None

    cur = conn.cursor()
    try:
        # Buscamos la dimensión y el puntaje para ese envío
        cur.execute(
            "SELECT dimension, puntaje FROM resultados WHERE envio_id = %s",
            (envio_id,)
        )

        filas = cur.fetchall()

        # Transformamos las filas de SQL en un diccionario de Python
        return {row[0]: float(row[1]) for row in filas}

    except Exception as e:
        print(f"Error al extraer datos: {e}")
        return None
    

def obtener_o_crear_usuario(nombre_usuario, email, empresa_id):
    conn = obtener_conexion()
    if not conn: return None
    cur = conn.cursor()

    try:
        # Intentamos buscar por email (que es el lado único)
        cur.execute(
            "SELECT id FROM usuarios WHERE email = %s;", (email,)
        )
        resultado = cur.fetchone()
        if resultado:
            return resultado[0]  # Retornamos el ID del usuario existente
        
        else:
            # Si no existe, lo creamos con su nombre, email y empresa
            cur.execute(
                "INSERT INTO usuarios (nombre_completo, email, empresa_id) VALUES (%s, %s, %s) RETURNING id;",
                (nombre_usuario, email, empresa_id)
            )
            user_id = cur.fetchone()[0]
            conn.commit()
            return user_id
    
    except Exception as e:
        # Imprimimos el error en tu consola para debugar
        print(f"Error en base de datos: {e}")
        return None
    

    finally:
        cur.close()
        conn.close()


def guardar_envio(usuario_id, test_id, servicio):
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        # Insertamos explícitamente el servicio y el estado inicial
        cur.execute("""
            INSERT INTO envios (usuario_id, test_id, fecha_finalizacion, servicio, estado_informe) 
            VALUES (%s, %s, CURRENT_TIMESTAMP, %s, 'Pendiente') 
            RETURNING id
        """, (usuario_id, test_id, servicio))
        
        envio_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return envio_id
    except Exception as e:
        st.error(f"Error al guardar el envío: {e}")
        return None


def listar_envios_con_nombres():
    """Trae una lista de envíos unidos con el nombre del usuario (SQL JOIN)."""
    conn = obtener_conexion()
    cur = conn.cursor()
    query = """
        SELECT e.id, u.nombre_completo, e.fecha_finalizacion 
        FROM envios e
        JOIN usuarios u ON e.usuario_id = u.id
        ORDER BY e.fecha_finalizacion DESC;
    """
    cur.execute(query)
    lista = cur.fetchall()
    cur.close()
    conn.close()
    return lista


def listar_empresas():
    # Trae el ID y Nombre de todas las empresas registradas
    conn = obtener_conexion()
    if not conn: return []
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM empresas ORDER BY nombre ASC;")
    empresas = cur.fetchall()
    cur.close()
    conn.close()
    return empresas


def obtener_promedio_empresas(empresa_id):

    # Calcularemos el promedio de DISC para todos los empleados de una empresa específica
    conn = obtener_conexion()
    if not conn: return None
    cur = conn.cursor()

    # Esta consulta une Resultados -> Envios -> Usuarios -> Empresas, filtrando por empresa_id
    query = """
        SELECT r.dimension, AVG(r.puntaje) as promedio
        FROM resultados r
        JOIN envios e ON r.envio_id = e.id
        JOIN usuarios u ON e.usuario_id = u.id
        WHERE u.empresa_id = %s
        GROUP BY r.dimension
        ORDER BY r.dimension ASC;
    """

    try:
        cur.execute(query, (empresa_id,))
        filas = cur.fetchall()
        # Convertimos a diccionario: {'C': 0.25, 'D': 0.30, 'I': 0.20, 'S': 0.25}
        return {row[0]: float(row[1]) for row in filas}
    
    except Exception as e:
        print(f"Error al calcular promedios: {e}")
        return None
    
    finally:
        cur.close()
        conn.close()


def eliminar_registro_usuario_completo(envio_id):
    """Borra un test, su usuario y, si queda vacía, la empresa."""
    conn = obtener_conexion()
    if not conn: return False
    cur = conn.cursor()
    try:
        # 1. Identificar usuario y empresa antes de borrar
        cur.execute("""
            SELECT u.id, u.empresa_id 
            FROM envios e 
            JOIN usuarios u ON e.usuario_id = u.id 
            WHERE e.id = %s
        """, (envio_id,))
        res = cur.fetchone()
        if not res: return False
        
        user_id, emp_id = res

        # 2. Borrar resultados y envío (esto suele ser CASCADE si lo configuraste, 
        # pero lo hacemos manual para asegurar)
        cur.execute("DELETE FROM resultados WHERE envio_id = %s;", (envio_id,))
        cur.execute("DELETE FROM envios WHERE id = %s;", (envio_id,))

        # 3. ¿Tiene el usuario más envíos? Si no, lo borramos
        cur.execute("SELECT COUNT(*) FROM envios WHERE usuario_id = %s;", (user_id,))
        if cur.fetchone()[0] == 0:
            cur.execute("DELETE FROM usuarios WHERE id = %s;", (user_id,))

        # 4. ¿Queda alguien en la empresa? Si no, la borramos
        cur.execute("SELECT COUNT(*) FROM usuarios WHERE empresa_id = %s;", (emp_id,))
        if cur.fetchone()[0] == 0:
            cur.execute("DELETE FROM empresas WHERE id = %s;", (emp_id,))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar registro: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def actualizar_estado_informe(envio_id, nuevo_estado):
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("""
            UPDATE envios 
            SET estado_informe = %s 
            WHERE id = %s
        """, (nuevo_estado, envio_id))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al actualizar estado: {e}")
        return False