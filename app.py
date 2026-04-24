# app.py
import streamlit as st
import re
from engine import calcular_resultados_disc
from database import obtener_password_test
from database import obtener_resultados_por_envio
from database import guardar_resultado_test
from database import listar_empresas
from reports import generar_pdf_disc
import datetime
from datetime import date
import plotly.graph_objects as go

st.set_page_config(page_title="Konantu - Plataforma de Diagnóstico", page_icon="Konantu_Fondo_Blanco.png", layout="wide")

# --- CONFIGURACIÓN GLOBAL DISC ---
COLORES_DISC = {'D': '#FF0000', 'I': '#FF9900', 'S': '#008000', 'C': '#0000FF'}
NOMBRES_DISC = {'D': 'Dominante', 'I': 'Influyente', 'S': 'Estable', 'C': 'Concienzudo'}
ORDEN_DISC = ['D', 'I', 'S', 'C']

# Textos descriptivos cortos para las tarjetas
DESCRIPCIONES_CORTAS = {
    'D': "Enfocado en resultados, toma decisiones rápidas y disfruta de los desafíos.",
    'I': "Optimista, entusiasta y orientado a las personas y la colaboración.",
    'S': "Paciente, leal y busca la armonía y estabilidad en su entorno.",
    'C': "Analítico, disciplinado y prioriza la calidad técnica y el orden."
}

# Las opciones están desordenadas para sincronizarse con config_disc.py
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
            "A": "Motivar al equipo y fomentar la participación creativa.",
            "B": "Ir directo al grano y definir objetivos claros.",
            "C": "Escuchar a todos y asegurar un ambiente de apoyo.",
            "D": "Seguir el orden del día y revisar los procedimientos."
        }
    },
    {
        "enunciado": "3. Ante un conflicto laboral, tiendo a:",
        "opciones": {
            "A": "Usar el humor o la persuasión para suavizar la situación.",
            "B": "Enfrentarlo directamente para resolverlo rápido.",
            "C": "Analizar las causas objetivas y basarme en las reglas.",
            "D": "Ceder o buscar un punto medio para evitar tensiones."
        }
    },
    {
        "enunciado": "4. ¿Qué frase te describe mejor?",
        "opciones": {
            "A": "Soy una persona optimista y comunicativa.",
            "B": "Soy una persona paciente y confiable.",
            "C": "Soy una persona decidida y competitiva.",
            "D": "Soy una persona precisa y disciplinada."
        }
    },
    {
        "enunciado": "5. Al trabajar en un proyecto priorizo:",
        "opciones": {
            "A": "La calidad técnica y la exactitud de los datos.",
            "B": "La estabilidad y el ritmo constante de trabajo.",
            "C": "La red de contactos y el reconocimiento del equipo.",
            "D": "La eficiencia y el cumplimiento de metas."
        }
    },
    {
        "enunciado": "6. ¿Cómo manejas los plazos ajustados?",
        "opciones": {
            "A": "Mantengo la calma y sigo el ritmo establecido.",
            "B": "Organizo cada minuto para no cometer errores por la prisa.",
            "C": "Trato de delegar o buscar ayuda de manera entusiasta.",
            "D": "Me presiono más para terminar a tiempo cueste lo que cueste."
        }
    },
    {
        "enunciado": "7. En eventos sociales, sueles:",
        "opciones": {
            "A": "Buscar personas clave para hacer contactos útiles.",
            "B": "Ser el centro de atención y conocer a mucha gente.",
            "C": "Observar el entorno y hablar solo si es necesario.",
            "D": "Conversar tranquilamente con personas conocidas."
        }
    },
    {
        "enunciado": "8. ¿Qué te frustra más?",
        "opciones": {
            "A": "Los cambios bruscos y los conflictos abiertos.",
            "B": "La falta de control y la ineficiencia.",
            "C": "El desorden y la falta de estándares claros.",
            "D": "El rechazo social y la rutina aburrida."
        }
    },
    {
        "enunciado": "9. Al recibir retroalimentación:",
        "opciones": {
            "A": "Pido detalles específicos y pruebas de lo que se dice.",
            "B": "La acepto si me ayuda a ganar o mejorar resultados.",
            "C": "Me importa mucho cómo afecta mi imagen personal.",
            "D": "La escucho con apertura si se dice de forma amable."
        }
    },
    {
        "enunciado": "10. En tu espacio de trabajo, prefieres:",
        "opciones": {
            "A": "Un espacio privado, funcional y muy organizado.",
            "B": "Un sitio tranquilo, ordenado y predecible.",
            "C": "Un ambiente dinámico, con desafíos constantes.",
            "D": "Un lugar colorido, abierto y con gente alrededor."
        }
    },
    {
        "enunciado": "11. ¿Cómo reaccionas ante un cambio repentino?",
        "opciones": {
            "A": "Lo veo como una oportunidad para liderar algo nuevo.",
            "B": "Me genera cierta inseguridad y necesito tiempo de ajuste.",
            "C": "Me adapto con curiosidad y busco el lado positivo.",
            "D": "Evalúo los riesgos y cómo afecta el plan original."
        }
    },
    {
        "enunciado": "12. Al resolver un problema complejo, tiendo a:",
        "opciones": {
            "A": "Tomar el mando y decidir el camino a seguir.",
            "B": "Investigar a fondo hasta encontrar la solución lógica.",
            "C": "Buscar métodos probados que hayan funcionado antes.",
            "D": "Hacer una lluvia de ideas creativa con otros."
        }
    },
    {
        "enunciado": "13. ¿Qué valoras más en un compañero?",
        "opciones": {
            "A": "Que sea alegre y colabore con energía.",
            "B": "Que sea competente y cuide los detalles técnicos.",
            "C": "Que sea leal y apoye al equipo en todo momento.",
            "D": "Que sea directo y cumpla con su parte."
        }
    },
    {
        "enunciado": "14. Si un proyecto se retrasa, tu prioridad es:",
        "opciones": {
            "A": "Asegurar que nadie se sienta sobrepasado por el estrés.",
            "B": "Identificar el error exacto que causó la demora.",
            "C": "Exigir resultados y acelerar el paso.",
            "D": "Mantener el ánimo del equipo arriba pese al retraso."
        }
    },
    {
        "enunciado": "15. En una negociación, tu estilo es:",
        "opciones": {
            "A": "Analítico, me baso en hechos y condiciones claras.",
            "B": "Dominante, busco ganar y cerrar el trato pronto.",
            "C": "Conciliador, busco que ambas partes estén cómodas.",
            "D": "Persuasivo, trato de convencer a través de la relación."
        }
    },
    {
        "enunciado": "16. ¿Cómo manejas las críticas a tu trabajo?",
        "opciones": {
            "A": "Me entristece si afecta mi relación con quien critica.",
            "B": "Las tomo con humildad y trato de mejorar poco a poco.",
            "C": "Las analizo lógicamente para ver si tienen fundamento real.",
            "D": "Me pongo a la defensiva si siento que cuestionan mi capacidad."
        }
    },
    {
        "enunciado": "17. Al planificar un viaje, prefieres:",
        "opciones": {
            "A": "Regresar a un lugar conocido que sea relajante.",
            "B": "Tener un itinerario detallado con horarios y reservas.",
            "C": "Ir a un lugar popular donde haya mucha diversión.",
            "D": "Decidir el destino y las actividades principales yo mismo."
        }
    },
    {
        "enunciado": "18. ¿Qué te motiva más en el trabajo?",
        "opciones": {
            "A": "El conocimiento experto y hacer las cosas bien.",
            "B": "La seguridad laboral y el buen clima interno.",
            "C": "El poder, la autoridad y alcanzar puestos altos.",
            "D": "El aplauso, el reconocimiento y la popularidad."
        }
    },
    {
        "enunciado": "19. Ante una tarea repetitiva, tu actitud es:",
        "opciones": {
            "A": "Me impaciento y busco cómo terminarla rápido.",
            "B": "La realizo de buena gana, me da tranquilidad.",
            "C": "Me aburro fácilmente y trato de socializar mientras la hago.",
            "D": "La hago con precisión para asegurar que no haya fallas."
        }
    },
    {
        "enunciado": "20. Si lideras un equipo, ¿qué harías primero?",
        "opciones": {
            "A": "Organizar una reunión para conocernos mejor.",
            "B": "Definir las reglas y estándares de calidad del grupo.",
            "C": "Asignar tareas y establecer metas ambiciosas.",
            "D": "Asegurarme de que todos tengan lo que necesitan para trabajar."
        }
    },
    {
        "enunciado": "21. ¿Cómo manejas los errores de otros?",
        "opciones": {
            "A": "Ayudo a corregirlos con paciencia y sin juzgar.",
            "B": "Los señalo con datos para evitar que se repitan.",
            "C": "Trato de no darle importancia para no dañar el clima.",
            "D": "Soy exigente y pido corrección inmediata."
        }
    },
    {
        "enunciado": "22. En una crisis, tu primera acción sería:",
        "opciones": {
            "A": "Tomar el control y dar órdenes claras.",
            "B": "Comunicar calma y mantener el optimismo del grupo.",
            "C": "Evaluar la situación con frialdad y buscar la causa.",
            "D": "Seguir los protocolos de seguridad establecidos."
        }
    },
    {
        "enunciado": "23. ¿Qué tipo de proyectos disfrutas más?",
        "opciones": {
            "A": "Proyectos técnicos que requieran gran especialización.",
            "B": "Proyectos a largo plazo con un equipo estable.",
            "C": "Proyectos creativos que involucren mucha gente.",
            "D": "Proyectos desafiantes con resultados tangibles."
        }
    },
    {
        "enunciado": "24. Al finalizar un día laboral, sueles:",
        "opciones": {
            "A": "Buscar a alguien para comentar cómo estuvo el día.",
            "B": "Desconectarte para disfrutar del tiempo en familia.",
            "C": "Revisar si todo quedó en su lugar y bien cerrado.",
            "D": "Pensar en lo que lograste y en los pendientes de mañana."
        }
    }
]

with st.sidebar:
    with st.sidebar:
        st.markdown("""<style>[data-testid="stSidebar"] {min-width: 260px; max-width: 260px;}</style>""", unsafe_allow_html=True)
        st.image("Konantu_Fondo_Blanco.png", width=180)
        st.title("Konantu - Acceso")
        st.write("---")

        pass_usuario_real = obtener_password_test()
        CLAVE_ADMIN = st.secrets["CLAVE_ADMIN"]

        password_general = st.text_input("Ingresa tu clave de acceso", type="password")
        
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
    
    if "datos_listos" not in st.session_state:
        st.session_state.datos_listos = False

    if not st.session_state.datos_listos:
        st.title("Sistema de Evaluación DISC - Konantu")
        st.write("Por favor, ingresa tus datos para comenzar")
        
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
            
            submit_registro = st.form_submit_button("Continuar a la Evaluación")
            
            if submit_registro:
                correo_es_valido = bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", st.session_state.email_usuario))
                if not st.session_state.nombre_usuario or not st.session_state.empresa_usuario:
                    st.error("Por favor, completa todos los campos (Nombre y Empresa).")
                elif not correo_es_valido:
                    st.error("El correo electrónico ingresado no es válido. Asegúrate de que no tenga espacios, incluya un arroba y termine con un dominio válido.")
                else:
                    st.session_state.datos_listos = True
                    
                    # Verificación en base de datos de envíos previos
                    from database import obtener_conexion
                    conn = obtener_conexion()
                    if conn:
                        cur = conn.cursor()
                        cur.execute("""
                            SELECT e.id, e.fecha_finalizacion
                            FROM usuarios u
                            JOIN envios e ON u.id = e.usuario_id
                            WHERE u.email = %s
                            ORDER BY e.fecha_finalizacion DESC
                            LIMIT 1
                        """, (st.session_state.email_usuario,))
                        envio_existente = cur.fetchone()
                        cur.close()
                        conn.close()
                        
                        if envio_existente:
                            envio_id = envio_existente[0]
                            fecha_prev = envio_existente[1]
                            resultados_previos = obtener_resultados_por_envio(envio_id)
                            
                            if resultados_previos:
                                st.session_state.test_finalizado = True
                                st.session_state.resultados_procesados = True
                                st.session_state.resultados_finales = resultados_previos
                                st.session_state.fecha_test = fecha_prev.strftime("%d/%m/%Y")
                                st.warning("El correo ingresado ya cuenta con una evaluación registrada. Redirigiendo a los resultados...")

                    st.rerun()

    if st.session_state.datos_listos:
        if "current_q" not in st.session_state:
            st.session_state.current_q = 0
        if "respuestas_temp" not in st.session_state:
            st.session_state.respuestas_temp = {}
        if "test_finalizado" not in st.session_state:
            st.session_state.test_finalizado = False

        if not st.session_state.test_finalizado:
            
            st.markdown("""<style>
            div[role="radiogroup"] > label > div:first-child { display: none !important; }
            div[role="radiogroup"] > label { background-color: #1e2520 !important; border: 1px solid #2d3830 !important; padding: 16px 24px !important; border-radius: 12px !important; margin-bottom: 12px !important; cursor: pointer !important; transition: all 0.2s ease !important; width: 100% !important; display: block !important; }
            div[role="radiogroup"] > label:hover { background-color: #263028 !important; border-color: #405244 !important; }
            div[role="radiogroup"] > label:has(input:checked) { background-color: #1a3322 !important; border: 2px solid #3e885b !important; box-shadow: 0 0 8px rgba(62, 136, 91, 0.4) !important; }
            div[role="radiogroup"] > label * { color: #ffffff !important; font-size: 16px !important; }
            button[kind="secondary"] { border-color: #2d3830 !important; background-color: transparent !important; color: #3e885b !important; }
            button[kind="secondary"]:hover { border-color: #3e885b !important; color: #4a9e6b !important; }
            </style>""", unsafe_allow_html=True)
            
            idx = st.session_state.current_q
            q_data = PREGUNTAS_DISC_DETALLADAS[idx]
            progress_pct = int(((idx + 1) / 24) * 100)

            # --- NUEVA ESTRUCTURA DE CABECERA (TÍTULO A LA IZQUIERDA, CONTADOR A LA DERECHA) ---
            col_head_left, col_head_right = st.columns([3, 1])
            
            with col_head_left:
                st.markdown(
                    "<h1 style='color: white; font-family: \"Georgia\", serif; font-style: italic; margin-bottom: 5px; font-size: 32px;'>Evaluación de Perfil Conductual</h1>"
                    "<p style='color: #6a96bc; font-size: 16px; margin-top: 0px;'>Cuestionario de Diagnóstico de Liderazgo y Colaboración</p>",
                    unsafe_allow_html=True
                )
                
            with col_head_right:
                html_progress = (
                    f"<div style='background-color: #161b17; border-radius: 12px; padding: 15px 25px; display: flex; align-items: center; justify-content: space-between; border: 1px solid #2a332c; margin-bottom: 30px; margin-left: auto; max-width: 220px;'>"
                    f"<div>"
                    f"<span style='color: #6a96bc; font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;'>PREGUNTAS</span><br>"
                    f"<span style='color: #3e885b; font-size: 22px; font-weight: bold;'>{idx + 1}</span>"
                    f"<span style='color: #556059; font-size: 16px;'> / 24</span>"
                    f"</div>"
                    f"<div style='position: relative; width: 45px; height: 45px;'>"
                    f"<svg viewBox='0 0 36 36' style='width: 45px; height: 45px;'>"
                    f"<path d='M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831' fill='none' stroke='#1d261f' stroke-width='4'/>"
                    f"<path stroke-dasharray='{progress_pct}, 100' d='M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831' fill='none' stroke='#2c5338' stroke-width='4' />"
                    f"<text x='18' y='21' fill='#ffffff' font-size='9' text-anchor='middle' font-weight='bold'>{progress_pct}%</text>"
                    f"</svg>"
                    f"</div>"
                    f"</div>"
                )
                st.markdown(html_progress, unsafe_allow_html=True)
            
            st.write("---")

            # Indicador verde de pregunta actual y enunciado limpio
            st.markdown(f"<div style='background-color: #1a3322; color: #3e885b; font-size: 11px; font-weight: bold; padding: 4px 10px; border-radius: 12px; display: inline-block; margin-bottom: 15px; letter-spacing: 1px;'>PREGUNTA {idx + 1}</div>", unsafe_allow_html=True)
            
            enunciado_limpio = q_data['enunciado'].split(". ", 1)[-1] if ". " in q_data['enunciado'] else q_data['enunciado']
            st.write(f"### {enunciado_limpio}")
            st.write("")

            opciones_keys = list(q_data['opciones'].keys())
            opciones_text = [f"**{k}**  |  {q_data['opciones'][k]}" for k in opciones_keys]
            current_ans_key = st.session_state.respuestas_temp.get(idx, None)
            index_default = opciones_keys.index(current_ans_key) if current_ans_key in opciones_keys else None
            seleccion = st.radio("Selecciona tu respuesta:", opciones_text, index=index_default, label_visibility="collapsed")
            
            st.write("---")
            col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
            
            with col_btn1:
                if idx > 0:
                    if st.button("Anterior", use_container_width=True):
                        if seleccion:
                            st.session_state.respuestas_temp[idx] = seleccion.replace("*", "").strip()[0]
                        st.session_state.current_q -= 1
                        st.rerun()
                        
            with col_btn3:
                if idx < 23:
                    if st.button("Siguiente", use_container_width=True):
                        if seleccion:
                            st.session_state.respuestas_temp[idx] = seleccion.replace("*", "").strip()[0]
                            st.session_state.current_q += 1
                            st.rerun()
                        else:
                            st.error("Selecciona una opción para avanzar.")
                else:
                    if st.button("Finalizar Encuesta", use_container_width=True, type="primary"):
                        if seleccion:
                            st.session_state.respuestas_temp[idx] = seleccion.replace("*", "").strip()[0]
                            if len(st.session_state.respuestas_temp) < 24:
                                st.error("Por favor, asegúrate de responder todas las preguntas.")
                            else:
                                st.session_state.test_finalizado = True
                                st.rerun()
                        else:
                            st.error("Selecciona una opción para finalizar.")

        else:
            from database import obtener_o_crear_usuario, obtener_o_crear_empresa, guardar_envio
            
            if not st.session_state.get("resultados_procesados", False):
                respuestas_usuario = [st.session_state.respuestas_temp[i] for i in range(24)]
                emp_id = obtener_o_crear_empresa(st.session_state.empresa_usuario)
                u_id = obtener_o_crear_usuario(st.session_state.nombre_usuario, st.session_state.email_usuario, emp_id)

                if u_id:
                    resultados = calcular_resultados_disc(respuestas_usuario)
                    st.session_state.fecha_test = date.today().strftime("%d/%m/%Y")
                    id_envio = guardar_envio(u_id, 1, st.session_state.tipo_servicio)
                    
                    if id_envio:
                        guardar_resultado_test(u_id, 1, resultados, id_envio)
                        st.session_state.resultados_finales = resultados
                        st.session_state.resultados_procesados = True
                        st.success(f"Test completado con éxito. ID de registro: {id_envio}")
                    else:
                        st.error("Error técnico: No se pudo registrar el envío en la base de datos.")
                else:
                    st.error("Error técnico: No se pudo registrar al usuario.")

            if st.session_state.get("resultados_procesados", False):
                final_scores = st.session_state.resultados_finales
                name = st.session_state.nombre_usuario
                diag_date = st.session_state.fecha_test
                rasgo_max = max(final_scores, key=final_scores.get)
                
                st.markdown("""<style>
                .main .block-container { padding-top: 2rem; }
                .k-card { background-color: #161b17; border: 1px solid #2a332c; border-radius: 12px; padding: 20px; color: white; opacity: 0.6; transition: all 0.3s; height: 100%; display: flex; flex-direction: column; justify-content: space-between; }
                .k-card.active { opacity: 1; border: 2px solid #3e885b; background-color: #1a251e; box-shadow: 0 4px 15px rgba(62, 136, 91, 0.2); }
                .k-badge { background-color: #3e885b; color: white; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; text-transform: uppercase; }
                .k-circle { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 20px; color: white; }
                .k-bar-bg { background-color: #2a332c; border-radius: 5px; height: 6px; width: 100%; margin-top: 5px; }
                </style>""", unsafe_allow_html=True)

                col_head1, col_head2 = st.columns([3, 1])
                with col_head1:
                    titulo_html = (
                        f"<h1 style='color: white; font-family: \"Georgia\", serif; font-style: italic; margin-bottom: 0px;'>Mi Perfil Conductual</h1>"
                        f"<p style='color: #6a96bc; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;'>FECHA DE DIAGNOSTICO: {diag_date} &nbsp;|&nbsp; {name}</p>"
                    )
                    st.markdown(titulo_html, unsafe_allow_html=True)
                with col_head2:
                    st.write("") 
                    pdf_file = generar_pdf_disc(name.strip(), final_scores)
                    with open(pdf_file, "rb") as file:
                        st.download_button(
                            label="EXPORTAR INFORME",
                            data=file,
                            file_name=f"Informe_DISC_{name.replace(' ','_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary"
                        )
                
                st.write("")

                col_chart1, col_chart2 = st.columns(2)
                
                val_d = int(round(final_scores.get('D', 0) * 24))
                val_i = int(round(final_scores.get('I', 0) * 24))
                val_s = int(round(final_scores.get('S', 0) * 24))
                val_c = int(round(final_scores.get('C', 0) * 24))

                with col_chart1:
                    fig_radar = go.Figure(go.Scatterpolar(
                        r=[val_d, val_i, val_s, val_c],
                        theta=['Dominante (D)', 'Influyente (I)', 'Estable (S)', 'Concienzudo (C)'],
                        fill='toself',
                        fillcolor='rgba(62, 136, 91, 0.4)',
                        line=dict(color='#3e885b', width=2)
                    ))
                    fig_radar.update_layout(
                        title=dict(text="EQUILIBRIO CONDUCTUAL", font=dict(color="#6a96bc", size=14)),
                        polar=dict(
                            bgcolor='#161b17',
                            radialaxis=dict(visible=True, range=[0, 24], gridcolor='#2a332c', tickfont=dict(color='#556059')),
                            angularaxis=dict(gridcolor='#2a332c', tickfont=dict(color='#a0a0a0'), linecolor='#2a332c')
                        ),
                        showlegend=False,
                        paper_bgcolor='#161b17',
                        plot_bgcolor='#161b17',
                        margin=dict(l=40, r=40, t=50, b=20),
                        height=350
                    )
                    st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})

                with col_chart2:
                    fig_bar = go.Figure(go.Bar(
                        x=['Dominante (D)', 'Influyente (I)', 'Estable (S)', 'Concienzudo (C)'],
                        y=[val_d, val_i, val_s, val_c],
                        marker_color=['#FF0000', '#FF9900', '#008000', '#0000FF'],
                        width=0.6
                    ))
                    fig_bar.update_layout(
                        title=dict(text="INTENSIDAD DE RASGOS", font=dict(color="#6a96bc", size=14)),
                        yaxis=dict(range=[0, 24], gridcolor='#2a332c', tickfont=dict(color='#556059'), dtick=6),
                        xaxis=dict(tickfont=dict(color='#a0a0a0'), linecolor='rgba(0,0,0,0)'),
                        paper_bgcolor='#161b17',
                        plot_bgcolor='#161b17',
                        margin=dict(l=20, r=20, t=50, b=20),
                        height=350
                    )
                    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

                st.write("")

                cols_cards = st.columns(4)
                
                for i, dim in enumerate(ORDEN_DISC):
                    val_raw = int(round(final_scores.get(dim, 0) * 24))
                    pct_width = int((val_raw / 24) * 100)
                    is_active = "active" if dim == rasgo_max else ""
                    badge_html = "<span class='k-badge'>PREDOMINANTE</span>" if dim == rasgo_max else ""
                    color = COLORES_DISC[dim]

                    html_card = (
                        f"<div class='k-card {is_active}'>"
                        f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;'>"
                        f"<div class='k-circle' style='background-color: {color};'>{dim}</div>"
                        f"{badge_html}"
                        f"</div>"
                        f"<h3 style='margin: 0; font-size: 18px;'>{NOMBRES_DISC[dim]}</h3>"
                        f"<p style='color: #a0a0a0; font-size: 12px; margin-top: 10px; line-height: 1.4;'>{DESCRIPCIONES_CORTAS[dim]}</p>"
                        f"<div style='margin-top: auto; padding-top: 20px;'>"
                        f"<div style='display: flex; justify-content: space-between; align-items: center;'>"
                        f"<span style='color: #6a96bc; font-size: 11px;'>Intensidad</span>"
                        f"<span style='font-weight: bold; font-size: 13px;'>{val_raw} / 24</span>"
                        f"</div>"
                        f"<div class='k-bar-bg'>"
                        f"<div style='background-color: {color}; width: {pct_width}%; height: 100%; border-radius: 5px;'></div>"
                        f"</div>"
                        f"</div>"
                        f"</div>"
                    )
                    with cols_cards[i]:
                        st.markdown(html_card, unsafe_allow_html=True)


elif rol == "Administrador":
    st.title("Panel de Administración - Konantu")
    st.write("Bienvenido. Aquí puedes revisar los test completados y generar los informes finales.")

    from database import listar_envios_con_nombres
    envios_disponibles = listar_envios_con_nombres()

    if envios_disponibles:
        with st.form("form_buscar_informe"):
            input_busqueda = st.text_input("Buscar evaluado por nombre: ", "")
            btn_buscar_info = st.form_submit_button("Buscar")
            
        if btn_buscar_info:
            st.session_state.filtro_informe = input_busqueda.lower()
            
        busqueda = st.session_state.get("filtro_informe", "")

        envios_filtrados = [env for env in envios_disponibles if busqueda in env[1].lower()]

        if envios_filtrados:
            opciones = {f"{env[1]} (fecha: {env[2].strftime('%d-%m-%Y')})":env[0] for env in envios_filtrados}
            seleccion = st.selectbox("Selecciona un test para procesar: ", list(opciones.keys()))

            id_final = opciones[seleccion]
            nombre_final = seleccion.split("(")[0]
            
            if st.button("Generar Informe para Revisión"):
                from database import obtener_resultados_por_envio
                from reports import generar_pdf_disc
                
                resultados_reales = obtener_resultados_por_envio(id_final)
                
                if resultados_reales:
                    archivo = generar_pdf_disc(nombre_final.strip(), resultados_reales)
                    with open(archivo, "rb") as file:
                        st.download_button(
                            label="Descargar Informe DISC Final",
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
    
    if lista_emp:
        opciones_emp = {emp[1]: emp[0] for emp in lista_emp}
        empresa_sel = st.selectbox("Selecciona una empresa para analizar el perfil grupal:", list(opciones_emp.keys()))
        id_empresa_sel = opciones_emp[empresa_sel]
        
        if st.button("Generar Dashboard del Equipo"):
            promedios = obtener_promedio_empresas(id_empresa_sel)
            if promedios:
                fig_barras = go.Figure()
                for dim in ORDEN_DISC:
                    val = promedios.get(dim, 0)
                    fig_barras.add_trace(go.Bar(
                        name=NOMBRES_DISC[dim], x=[NOMBRES_DISC[dim]], y=[val * 100],
                        marker_color=COLORES_DISC[dim], text=[f"{int(val*100)}%"], textposition='auto',
                    ))
                fig_barras.update_layout(title=f"PERFIL PROMEDIO: {empresa_sel.upper()}", yaxis=dict(range=[0, 100]), showlegend=False)
                st.plotly_chart(fig_barras, use_container_width=True)
                
                predominante_equipo = max(promedios, key=promedios.get)
                st.info(f"Cultura de Equipo: La empresa '{empresa_sel}' tiene una tendencia hacia la {NOMBRES_DISC[predominante_equipo]}.")
            else:
                st.info("No se han encontrado registros de test completados para esta empresa.")


        st.write("---")
        st.subheader("Gestión de Eliminación de Registros")

        with st.form("form_buscar_eliminar"):
            input_eliminar = st.text_input("Buscar evaluado para eliminar (Nombre completo o parcial):", key="search_delete")
            btn_buscar_eliminar = st.form_submit_button("Buscar Registro")
            
        if btn_buscar_eliminar:
            st.session_state.filtro_eliminar = input_eliminar
            
        nombre_a_buscar = st.session_state.get("filtro_eliminar", "")

        if nombre_a_buscar:
            from database import obtener_conexion
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
                opciones_borrar = {f"ID: {c[0]} | {c[1]} ({c[2]})": c[0] for c in coincidencias}
                seleccion_borrar = st.selectbox("Selecciona el registro específico a eliminar:", options=list(opciones_borrar.keys()))
                id_a_borrar = opciones_borrar[seleccion_borrar]
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
        query = """
            SELECT e.fecha_finalizacion as "Fecha", u.nombre_completo as "Evaluado", u.email as "Correo",
                em.nombre as "Empresa", e.servicio as "Plan Contratado",
                MAX(CASE WHEN r.dimension = 'D' THEN r.puntaje END) * 100 as "D",
                MAX(CASE WHEN r.dimension = 'I' THEN r.puntaje END) * 100 as "I",
                MAX(CASE WHEN r.dimension = 'S' THEN r.puntaje END) * 100 as "S",
                MAX(CASE WHEN r.dimension = 'C' THEN r.puntaje END) * 100 as "C"
            FROM envios e JOIN usuarios u ON e.usuario_id = u.id JOIN empresas em ON u.empresa_id = em.id
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
                st.success("Datos listos.")
                st.download_button(label="Descargar archivo .xlsx", data=buffer.getvalue(), file_name=f"Ventas_Konantu_{datetime.date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.warning("No hay datos disponibles para exportar.")
        except Exception as e:
            st.error(f"Error técnico: {e}")

    st.write("---")
    st.subheader("Gestión de Informes Premium ($20.000)")

    from database import obtener_conexion, actualizar_estado_informe
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT e.id, u.nombre_completo, e.fecha_finalizacion, e.estado_informe
        FROM envios e JOIN usuarios u ON e.usuario_id = u.id
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
                    st.error("Pendiente")
                else:
                    st.success("Enviado")
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
    st.subheader("Configuración de Seguridad")
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
    col_left, col_cent, col_right = st.columns([0.5, 2, 0.5])
    with col_cent:
        st.markdown("<h1 style='text-align: center;'>Bienvenido a Konantu</h1>", unsafe_allow_html=True)
        st.write("---")
        st.markdown("""
            <div style="background-color: #1E1E1E; color: #00f2ff; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #333;">
                Por favor, ingresa tu contraseña de acceso en el panel lateral para comenzar.
            </div>
        """, unsafe_allow_html=True)
        st.write("") 
        st.image("Konantu_Fondo_Blanco.png", use_container_width=True)