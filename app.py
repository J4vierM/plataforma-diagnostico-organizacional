# app.py
import streamlit as st
from engine import calcular_resultados_disc
from database import obtener_password_test
from database import obtener_resultados_por_envio
from database import guardar_resultado_test
from database import listar_empresas
from reports import generar_pdf_disc
import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Konantu - Plataforma de Diagnóstico", page_icon = "Konantu_Fondo_Blanco.png")


# --- CONFIGURACIÓN GLOBAL DISC ---
COLORES_DISC = {'D': '#FF0000', 'I': '#FF9900', 'S': '#008000', 'C': '#0000FF'}
NOMBRES_DISC = {'D': 'Dominante', 'I': 'Influyente', 'S': 'Estable', 'C': 'Concienzudo'}
ORDEN_DISC = ['D', 'I', 'S', 'C']

def mostrar_dashboard_estilo_excel(resultados, titulo_grafico="GRÁFICO DE PERFIL DISC"):
    import plotly.graph_objects as go
    
    # 1. Gráfico de Barras
    fig_barras = go.Figure()
    for dim in ORDEN_DISC:
        val = resultados.get(dim, 0)
        fig_barras.add_trace(go.Bar(
            name=NOMBRES_DISC[dim],
            x=[NOMBRES_DISC[dim]],
            y=[val * 100],
            marker_color=COLORES_DISC[dim],
            text=[f"{int(val*100)}%"],
            textposition='auto',
        ))

    fig_barras.update_layout(
        title=titulo_grafico,
        yaxis=dict(range=[0, 100], title="Porcentaje (%)"),
        xaxis=dict(tickangle=0),
        template="plotly_white",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_barras, use_container_width=True)

    # 2. Semicírculos (Gauges)
    st.write("### Puntaje por Rasgo")
    cols = st.columns(4)
    for i, dim in enumerate(ORDEN_DISC):
        val = resultados.get(dim, 0)
        with cols[i]:
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = val * 100,
                number = {'suffix': "", 'font': {'size': 20}},
                title = {'text': NOMBRES_DISC[dim], 'font': {'size': 16, 'color': COLORES_DISC[dim]}},
                gauge = {
                    'axis': {'range': [0, 100], 'tickvals': [0, 50, 100], 'ticktext': ['0', '50', '100'], 'tickwidth': 1},
                    'bar': {'color': COLORES_DISC[dim]},
                    'bgcolor': "#f0f0f0",
                }
            ))
            fig_gauge.update_layout(height=200, margin=dict(l=30, r=30, t=50, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

# Las opciones son siempre las mismas A, B, C, D
PREGUNTAS_DISC_DETALLADAS = [
    {
        "enunciado": "1. ¿Cómo sueles tomar decisiones importantes?",
        "opciones": {
            "A": "Rápidamente, enfocándome en los resultados inmediatos.",
            "B": "De forma entusiasta, considerando el impacto en las personas.",
            "C": "Con calma, buscando el consenso y la armonía del grupo.",
            "D": "Analizando todos los datos y detalles antes de actuar."
        }
    },
    {
        "enunciado": "2. En una reunión en equipo, prefiero:",
        "opciones": {
            "A": "Ir directo al grano y definir objetivos claros.",
            "B": "Motivar al equipo y fomentar la participación creativa.",
            "C": "Escuchar a todos y asegurar un ambiente de apoyo.",
            "D": "Seguir el orden del día y revisar los procedimientos."
        }
    },
    {
        "enunciado": "3. Ante un conflicto laboral, tiendo a:",
        "opciones": {
            "A": "Enfrentarlo directamente para resolverlo rápido.",
            "B": "Usar el humor o la persuasión para suavizar la situación.",
            "C": "Cededer o buscar un punto medio para evitar tensiones.",
            "D": "Analizar las causas objetivas y basarme en las reglas."
        }
    },
    {
        "enunciado": "4. ¿Qué frase te describe mejor?",
        "opciones": {
            "A": "Soy una persona decidida y competitiva.",
            "B": "Soy una persona optimista y comunicativa.",
            "C": "Soy una persona paciente y confiable.",
            "D": "Soy una persona precisa y disciplinada."
        }
    },
    {
        "enunciado": "5. Al trabajar en un proyecto priorizo:",
        "opciones": {
            "A": "La eficiencia y el cumplimiento de metas.",
            "B": "La red de contactos y el reconocimiento del equipo.",
            "C": "La estabilidad y el ritmo constante de trabajo.",
            "D": "La calidad técnica y la exactitud de los datos."
        }
    },
    {
        "enunciado": "6. ¿Cómo manejas los plazos ajustados?",
        "opciones": {
            "A": "Me presiono más para terminar a tiempo cueste lo que cueste.",
            "B": "Trato de delegar o buscar ayuda de manera entusiasta.",
            "C": "Mantengo la calma y sigo el ritmo establecido.",
            "D": "Organizo cada minuto para no cometer errores por la prisa."
        }
    },
    {
        "enunciado": "7. En eventos sociales, sueles:",
        "opciones": {
            "A": "Buscar personas clave para hacer contactos útiles.",
            "B": "Ser el centro de atención y conocer a mucha gente.",
            "C": "Conversar tranquilamente con personas conocidas.",
            "D": "Observar el entorno y hablar solo si es necesario."
        }
    },
    {
        "enunciado": "8. ¿Qué te frustra más?",
        "opciones": {
            "A": "La falta de control y la ineficiencia.",
            "B": "El rechazo social y la rutina aburrida.",
            "C": "Los cambios bruscos y los conflictos abiertos.",
            "D": "El desorden y la falta de estándares claros."
        }
    },
    {
        "enunciado": "9. Al recibir retroalimentación:",
        "opciones": {
            "A": "La acepto si me ayuda a ganar o mejorar resultados.",
            "B": "Me importa mucho cómo afecta mi imagen personal.",
            "C": "La escucho con apertura si se dice de forma amable.",
            "D": "Pido detalles específicos y pruebas de lo que se dice."
        }
    },
    {
        "enunciado": "10. En tu espacio de trabajo, prefieres:",
        "opciones": {
            "A": "Un ambiente dinámico, con desafíos constantes.",
            "B": "Un lugar colorido, abierto y con gente alrededor.",
            "C": "Un sitio tranquilo, ordenado y predecible.",
            "D": "Un espacio privado, funcional y muy organizado."
        }
    },
    {
        "enunciado": "11. ¿Cómo reaccionas ante un cambio repentino?",
        "opciones": {
            "A": "Lo veo como una oportunidad para liderar algo nuevo.",
            "B": "Me adapto con curiosidad y busco el lado positivo.",
            "C": "Me genera cierta inseguridad y necesito tiempo de ajuste.",
            "D": "Evalúo los riesgos y cómo afecta el plan original."
        }
    },
    {
        "enunciado": "12. Al resolver un problema complejo, tiendo a:",
        "opciones": {
            "A": "Tomar el mando y decidir el camino a seguir.",
            "B": "Hacer una lluvia de ideas creativa con otros.",
            "C": "Buscar métodos probados que hayan funcionado antes.",
            "D": "Investigar a fondo hasta encontrar la solución lógica."
        }
    },
    {
        "enunciado": "13. ¿Qué valoras más en un compañero?",
        "opciones": {
            "A": "Que sea directo y cumpla con su parte.",
            "B": "Que sea alegre y colabore con energía.",
            "C": "Que sea leal y apoye al equipo en todo momento.",
            "D": "Que sea competente y cuide los detalles técnicos."
        }
    },
    {
        "enunciado": "14. Si un proyecto se retrasa, tu prioridad es:",
        "opciones": {
            "A": "Exigir resultados y acelerar el paso.",
            "B": "Mantener el ánimo del equipo arriba pese al retraso.",
            "C": "Asegurar que nadie se sienta sobrepasado por el estrés.",
            "D": "Identificar el error exacto que causó la demora."
        }
    },
    {
        "enunciado": "15. En una negociación, tu estilo es:",
        "opciones": {
            "A": "Dominante, busco ganar y cerrar el trato pronto.",
            "B": "Persuasivo, trato de convencer a través de la relación.",
            "C": "Conciliador, busco que ambas partes estén cómodas.",
            "D": "Analítico, me baso en hechos y condiciones claras."
        }
    },
    {
        "enunciado": "16. ¿Cómo manejas las críticas a tu trabajo?",
        "opciones": {
            "A": "Me pongo a la defensiva si siento que cuestionan mi capacidad.",
            "B": "Me entristece si afecta mi relación con quien critica.",
            "C": "Las tomo con humildad y trato de mejorar poco a poco.",
            "D": "Las analizo lógicamente para ver si tienen fundamento real."
        }
    },
    {
        "enunciado": "17. Al planificar un viaje, prefieres:",
        "opciones": {
            "A": "Decidir el destino y las actividades principales yo mismo.",
            "B": "Ir a un lugar popular donde haya mucha diversión.",
            "C": "Regresar a un lugar conocido que sea relajante.",
            "D": "Tener un itinerario detallado con horarios y reservas."
        }
    },
    {
        "enunciado": "18. ¿Qué te motiva más en el trabajo?",
        "opciones": {
            "A": "El poder, la autoridad y alcanzar puestos altos.",
            "B": "El aplauso, el reconocimiento y la popularidad.",
            "C": "La seguridad laboral y el buen clima interno.",
            "D": "El conocimiento experto y hacer las cosas bien."
        }
    },
    {
        "enunciado": "19. Ante una tarea repetitiva, tu actitud es:",
        "opciones": {
            "A": "Me impaciento y busco cómo terminarla rápido.",
            "B": "Me aburro fácilmente y trato de socializar mientras la hago.",
            "C": "La realizo de buena gana, me da tranquilidad.",
            "D": "La hago con precisión para asegurar que no haya fallas."
        }
    },
    {
        "enunciado": "20. Si lideras un equipo, ¿qué harías primero?",
        "opciones": {
            "A": "Asignar tareas y establecer metas ambiciosas.",
            "B": "Organizar una reunión para conocernos mejor.",
            "C": "Asegurarme de que todos tengan lo que necesitan para trabajar.",
            "D": "Definir las reglas y estándares de calidad del grupo."
        }
    },
    {
        "enunciado": "21. ¿Cómo manejas los errores de otros?",
        "opciones": {
            "A": "Soy exigente y pido corrección inmediata.",
            "B": "Trato de no darle importancia para no dañar el clima.",
            "C": "Ayudo a corregirlos con paciencia y sin juzgar.",
            "D": "Los señalo con datos para evitar que se repitan."
        }
    },
    {
        "enunciado": "22. En una crisis, tu primera acción sería:",
        "opciones": {
            "A": "Tomar el control y dar órdenes claras.",
            "B": "Comunicar calma y mantener el optimismo del grupo.",
            "C": "Seguir los protocolos de seguridad establecidos.",
            "D": "Evaluar la situación con frialdad y buscar la causa."
        }
    },
    {
        "enunciado": "23. ¿Qué tipo de proyectos disfrutas más?",
        "opciones": {
            "A": "Proyectos desafiantes con resultados tangibles.",
            "B": "Proyectos creativos que involucren mucha gente.",
            "C": "Proyectos a largo plazo con un equipo estable.",
            "D": "Proyectos técnicos que requieran gran especialización."
        }
    },
    {
        "enunciado": "24. Al finalizar un día laboral, sueles:",
        "opciones": {
            "A": "Pensar en lo que lograste y en los pendientes de mañana.",
            "B": "Buscar a alguien para comentar cómo estuvo el día.",
            "C": "Desconectarte para disfrutar del tiempo en familia.",
            "D": "Revisar si todo quedó en su lugar y bien cerrado."
        }
    }
]

#Descripciones detalladas para el usuario final.
DESCRIPCIONES_DISC = {
    'D': "**Tu rasgo predominante es la Dominancia:** Eres una persona orientada a resultados, decidida y competitiva. Te motivan los desafíos y tienes una gran capacidad para tomar el mando en situaciones críticas.",
    'I': "**Tu rasgo predominante es la Influencia:** Eres una persona entusiasta, optimista y comunicativa. Tu fortaleza reside en la capacidad de persuadir y motivar a los demás a través de las relaciones.",
    'S': "**Tu rasgo predominante es la Estabilidad:** Eres una persona paciente, leal y persistente. Valoras la armonía en el equipo y eres un excelente oyente, brindando seguridad y constancia al entorno laboral.",
    'C': "**Tu rasgo predominante es el Cumplimiento:** Eres una persona precisa, analítica y disciplinada. Te enfocas en la calidad y en seguir los estándares, asegurando que las tareas se realicen con el mayor rigor técnico."
}

with st.sidebar:
    # 1. Estilo para el ancho de la barra (CSS)
    with st.sidebar:
        st.markdown("""<style>[data-testid="stSidebar"] {min-width: 260px; max-width: 260px;}</style>""", unsafe_allow_html=True)
        st.image("Konantu_Fondo_Blanco.png", width=180)
        st.title("Konantu - Acceso")
        st.write("---")

    # 1. Traemos las claves para comparar
        pass_usuario_real = obtener_password_test()
        CLAVE_ADMIN = st.secrets["CLAVE_ADMIN"]

    # 2. ÚNICA caja de entrada para todos
        password_general = st.text_input("Ingresa tu clave de acceso", type="password")
        
        # 3. Determinamos el ROL según la clave
        rol = None
        if password_general == CLAVE_ADMIN:
            st.success("Modo Administrador")
            rol = st.selectbox("Seleccionar Vista", ["Administrador", "Evaluación DISC"])
        elif password_general == pass_usuario_real:
            st.success("Modo Evaluación DISC")
            rol = "Evaluación DISC"
        elif password_general != "":
            st.error("Clave incorrecta")

    st.write("---")


if rol == "Evaluación DISC":
    enviado = False # Inicializamos para evitar NameError
    st.title("Sistema de Evaluación DISC - Konantu")
    st.write("Por favor, ingresa tus datos para comenzar")

# --- NUEVO BLOQUE DE REGISTRO CON FORMULARIO ---
    if "datos_listos" not in st.session_state:
        st.session_state.datos_listos = False

    if not st.session_state.datos_listos:
        with st.form("form_registro"):
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.nombre_usuario = st.text_input("Nombre Completo")
                st.session_state.email_usuario = st.text_input("Correo Electrónico")
            with col2:
                st.session_state.empresa_usuario = st.text_input("Nombre de tu Empresa")
                st.session_state.tipo_servicio = st.selectbox(
                    "Plan Contratado",
                    ["Básico ($15.000 - Solo Dashboard)", "Premium ($20.000 - Informe Detallado + Diagnóstico)"]
                )
            if st.form_submit_button("Continuar a la Evaluación"):
                if st.session_state.nombre_usuario and "@" in st.session_state.email_usuario and st.session_state.empresa_usuario:
                    st.session_state.datos_listos = True
                    st.rerun()
                else:
                    st.error("Por favor, completa todos los campos correctamente.")

    # Mostramos el test solo cuando los datos iniciales están confirmados
    if st.session_state.datos_listos:
        # Recuperamos las variables para mantener intacta tu lógica de guardado SQL
        nombre_usuario = st.session_state.nombre_usuario
        email_usuario = st.session_state.email_usuario
        empresa_usuario = st.session_state.empresa_usuario
        tipo_servicio = st.session_state.tipo_servicio

        with st.form("test_disc"):
            for i, item in enumerate(PREGUNTAS_DISC_DETALLADAS, 1):
                st.write(f"#### {item['enunciado']}")
                opciones_mostrar = [f"{letra}) {texto}" for letra, texto in item["opciones"].items()]
                st.radio("Selecciona:", opciones_mostrar, key=f"p{i}", label_visibility="collapsed")
                st.write("---")
            enviado = st.form_submit_button("Finalizar y Guardar Resultados")

        if enviado:
            # Aquí sigue tu lógica de procesamiento de respuestas (Línea 304 de tu código original)
            respuestas_usuario = [st.session_state[f"p{i}"][0] for i in range(1, 25)]
            from database import obtener_o_crear_usuario, obtener_o_crear_empresa, guardar_envio
            
            emp_id = obtener_o_crear_empresa(empresa_usuario)
            u_id = obtener_o_crear_usuario(nombre_usuario, email_usuario, emp_id)

            if u_id:
                st.session_state.usuario_id = u_id
                resultados = calcular_resultados_disc(respuestas_usuario)
                id_envio = guardar_envio(u_id, 1, tipo_servicio)
                
                if id_envio:
                    guardar_resultado_test(u_id, 1, resultados, id_envio)
                    st.success(f"¡Test completado con éxito! ID: {id_envio}")
                    st.balloons()
                    mostrar_dashboard_estilo_excel(resultados)
                    rasgo_max = max(resultados, key=resultados.get)
                    st.info(DESCRIPCIONES_DISC[rasgo_max])
                else:
                    st.error("Error técnico: No se pudo registrar al usuario.")



elif rol == "Administrador":
    # Vista dad
    st.title("Panel de Administración - Konantu")
    st.write("Bienvenido. Aquí puedes revisar los test completados y generar los informes finales.")

    from database import listar_envios_con_nombres
    envios_disponibles = listar_envios_con_nombres()

    if envios_disponibles:

# --- NUEVO BUSCADOR DE INFORMES ---
        with st.form("form_buscar_informe"):
            input_busqueda = st.text_input("Buscar evaluado por nombre: ", "")
            btn_buscar_info = st.form_submit_button("Buscar")
            
        if btn_buscar_info:
            st.session_state.filtro_informe = input_busqueda.lower()
            
        busqueda = st.session_state.get("filtro_informe", "")

        # 2. Filtramos la lista según la búsqueda confirmada
        envios_filtrados = [
            env for env in envios_disponibles
            if busqueda in env[1].lower()
        ]

        if envios_filtrados:
            # Creamos las opciones olo con los resultados del buscador
            opciones = {f"{env[1]} (fecha: {env[2].strftime('%d-%m-%Y')})":env[0] for env in envios_filtrados}
            seleccion = st.selectbox("Selecciona un test para procesar: ", list(opciones.keys()))

            id_final = opciones[seleccion]
            nombre_final = seleccion.split("(")[0]
            
            if st.button("Generar Informe para Revisión"):
                # 1. Importamos las funciones necesarias
                from database import obtener_resultados_por_envio
                from reports import generar_pdf_disc
                
                # 2. Traemos los datos REALES desde SQL usando el ID que seleccionaste
                resultados_reales = obtener_resultados_por_envio(id_final)
                
                if resultados_reales:
                    # 3. Creamos el PDF con el nombre y los datos reales
                    archivo = generar_pdf_disc(nombre_final.strip(), resultados_reales)
                    
                    # 4. Creamos el botón de descarga
                    with open(archivo, "rb") as file:
                        st.download_button(
                            label="⬇️ Descargar Informe DISC Final",
                            data=file,
                            file_name=archivo,
                            mime="application/pdf"
                        )
                    st.success(f"Informe de {nombre_final} listo para descargar.")
                else:
                    st.error(f"No se encontraron datos para el ID {id_final} en la base de datos.")
            
    from database import listar_empresas, obtener_promedio_empresas

    lista_emp = listar_empresas()

    st.write("---")
    st.subheader("Análisis Grupal por Empresa")
    
    from database import listar_empresas, obtener_promedio_empresas
    lista_emp = listar_empresas()
    
    if lista_emp:
        # Creamos el diccionario para el selector
        opciones_emp = {emp[1]: emp[0] for emp in lista_emp}
        empresa_sel = st.selectbox("Selecciona una empresa para analizar el perfil grupal:", list(opciones_emp.keys()))
        id_empresa_sel = opciones_emp[empresa_sel]
        
        if st.button("Generar Dashboard del Equipo"):
            promedios = obtener_promedio_empresas(id_empresa_sel)
            
            if promedios:
                # REUTILIZAMOS tu función estética con los colores D-I-S-C
                mostrar_dashboard_estilo_excel(
                    promedios, 
                    titulo_grafico=f"PERFIL PROMEDIO: {empresa_sel.upper()}"
                )
                
                # Análisis rápido para el consultor
                predominante_equipo = max(promedios, key=promedios.get)
                st.info(f"💡 **Cultura de Equipo:** La empresa '{empresa_sel}' tiene una tendencia hacia la **{NOMBRES_DISC[predominante_equipo]}**.")
            else:
                st.info("No se han encontrado registros de test completados para esta empresa.")


        st.write("---")
        st.subheader("Gestión de Eliminación de Registros")

        # 1. Buscador específico para borrar
        # --- NUEVO BUSCADOR PARA ELIMINAR ---
        with st.form("form_buscar_eliminar"):
            input_eliminar = st.text_input("Buscar evaluado para eliminar (Nombre completo o parcial):", key="search_delete")
            btn_buscar_eliminar = st.form_submit_button("Buscar Registro")
            
        if btn_buscar_eliminar:
            st.session_state.filtro_eliminar = input_eliminar
            
        nombre_a_buscar = st.session_state.get("filtro_eliminar", "")

        if nombre_a_buscar:
            from database import obtener_conexion
            
            # Buscamos coincidencias en la DB para dar opciones claras
            conn = obtener_conexion()
            cur = conn.cursor()
            cur.execute("""
                SELECT e.id, u.nombre_completo, em.nombre 
                FROM envios e
                JOIN usuarios u ON e.usuario_id = u.id
                JOIN empresas em ON u.empresa_id = em.id
                WHERE UPPER(u.nombre_completo) LIKE UPPER(%s)
                ORDER BY e.id DESC
            """, (f"%{nombre_a_buscar}%",))
            
            coincidencias = cur.fetchall()
            cur.close()
            conn.close()

            if coincidencias:
                # Creamos un diccionario para que el admin elija el registro exacto
                # Formato: "ID: 24 | Nombre: Javier | Empresa: Konantu"
                opciones_borrar = {f"ID: {c[0]} | {c[1]} ({c[2]})": c[0] for c in coincidencias}
                
                seleccion_borrar = st.selectbox(
                    "Selecciona el registro específico a eliminar:",
                    options=list(opciones_borrar.keys())
                )
                
                id_a_borrar = opciones_borrar[seleccion_borrar]
                
                # 2. Botón de confirmación con advertencia visual
                st.warning(f"¿Estás seguro de que deseas eliminar permanentemente el registro {seleccion_borrar}?")
                
                if st.button(f"Confirmar Eliminación de {seleccion_borrar}", type="primary"):
                    from database import eliminar_registro_usuario_completo
                    import time
                    
                    if eliminar_registro_usuario_completo(id_a_borrar):
                        st.success("Registro eliminado correctamente.")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Hubo un error al intentar eliminar el registro.")
            else:
                st.info("No se encontraron registros que coincidan con ese nombre.")

    st.write("---")
    st.subheader("Descarga de Datos para Gestión")

    if st.button("Generar Reporte Excel de Ventas"):
        from database import obtener_conexion
        import pandas as pd
        import io

        conn = obtener_conexion()
        # Traemos toda la data relevante para el negocio
        query = """
            SELECT 
                e.fecha_finalizacion as "Fecha", 
                u.nombre_completo as "Evaluado",
                u.email as "Correo",
                em.nombre as "Empresa",
                e.servicio as "Plan Contratado",
                MAX(CASE WHEN r.dimension = 'D' THEN r.puntaje END) * 100 as "D",
                MAX(CASE WHEN r.dimension = 'I' THEN r.puntaje END) * 100 as "I",
                MAX(CASE WHEN r.dimension = 'S' THEN r.puntaje END) * 100 as "S",
                MAX(CASE WHEN r.dimension = 'C' THEN r.puntaje END) * 100 as "C"
            FROM envios e
            JOIN usuarios u ON e.usuario_id = u.id
            JOIN empresas em ON u.empresa_id = em.id
            JOIN resultados r ON r.envio_id = e.id
            GROUP BY e.id, e.fecha_finalizacion, u.nombre_completo, u.email, em.nombre, e.servicio
            ORDER BY e.fecha_finalizacion DESC
        """
        
        try:
            df = pd.read_sql(query, conn)
            conn.close()

            if not df.empty:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Resultados Konantu')
                
                # Mostramos el botón de descarga
                st.success("✅ ¡Datos listos!")
                st.download_button(
                    label="💾 Descargar archivo .xlsx",
                    data=buffer.getvalue(),
                    file_name=f"Ventas_Konantu_{datetime.date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("No hay datos disponibles para exportar.")
                
        except Exception as e:
            st.error(f"Error técnico: {e}")

    st.write("---")
    st.subheader("📬 Gestión de Informes Premium ($20.000)")

    from database import obtener_conexion, actualizar_estado_informe
    conn = obtener_conexion()
    cur = conn.cursor()
    # Solo buscamos los que contrataron el plan premium
    cur.execute("""
        SELECT e.id, u.nombre_completo, e.fecha_finalizacion, e.estado_informe
        FROM envios e
        JOIN usuarios u ON e.usuario_id = u.id
        WHERE e.servicio LIKE '%$20.000%'
        ORDER BY CASE WHEN e.estado_informe = 'Pendiente' THEN 1 ELSE 2 END, e.fecha_finalizacion DESC
    """)
    pendientes = cur.fetchall()
    cur.close()
    conn.close()

    if pendientes:
        for p in pendientes:
            envio_id, nombre, fecha, estado = p
            col_info, col_status, col_accion = st.columns([2, 1, 1])
            
            with col_info:
                st.write(f"**{nombre}**")
                st.caption(f"Terminado el: {fecha.strftime('%d/%m/%Y %H:%M')}")
            
            with col_status:
                if estado == 'Pendiente':
                    st.error("🔴 Pendiente")
                else:
                    st.success("🟢 Enviado")
            
            with col_accion:
                if estado == 'Pendiente':
                    if st.button("Marcar como Enviado", key=f"btn_{envio_id}"):
                        if actualizar_estado_informe(envio_id, 'Enviado'):
                            st.rerun()
                else:
                    st.write("Completado")

    else:
        st.info("No hay informes premium pendientes por gestionar.")

    st.write("---")
    st.subheader("⚙️ Configuración de Seguridad")
    nueva_pass = st.text_input("Actualizar Contraseña para Alumnos", value=pass_usuario_real)
    if st.button("Guardar Nueva Contraseña"):
        from database import obtener_conexion
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("UPDATE configuracion SET valor = %s WHERE clave = 'password_diaria'", (nueva_pass,))
        conn.commit()
        cur.close()
        conn.close()
        st.success(f"Contraseña actualizada a: {nueva_pass}")



elif rol is None:
    # 1. Creamos 3 columnas: la del medio (col_cent) es donde irá todo
    # El ratio [0.5, 2, 0.5] deja espacios iguales a los lados.
    col_left, col_cent, col_right = st.columns([0.5, 2, 0.5])
    
    with col_cent:
        # 2. Título centrado con HTML
        st.markdown("<h1 style='text-align: center;'>Bienvenido a Konantu</h1>", unsafe_allow_html=True)
        st.write("---")
        
        # 3. Cuadro de información centrado
        st.markdown("""
            <div style="background-color: #1E1E1E; color: #00f2ff; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #333;">
                👋 Por favor, ingresa tu contraseña de acceso en el panel lateral para comenzar.
            </div>
        """, unsafe_allow_html=True)
        
        st.write("") # Espacio estético
        
        # 4. Imagen centrada
        # Al estar dentro de 'col_cent', la imagen se ajustará al ancho de esa columna
        st.image("Konantu_Fondo_Blanco.png", use_container_width=True)



