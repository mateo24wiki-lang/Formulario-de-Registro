import streamlit as st
import re
from io import BytesIO

# Intentamos importar qrcode y Pillow de forma segura
try:
    import qrcode
    from PIL import Image as PilImage
    QR_LIB_AVAILABLE = True
except Exception:
    qrcode = None
    PilImage = None
    QR_LIB_AVAILABLE = False

# Formulario de Registro de Mascotas (ejecutable)
# Ejecutar: streamlit run formulario.py

st.title("Formulario de Registro de Mascotas")

# Inicializar session state para mantener el estado del formulario
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
    st.session_state.form_data = {}

with st.form(key="registro_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Datos de la Mascota")
        nombre_mascota = st.text_input("Nombre de la mascota")
        tipo_mascota = st.selectbox("Tipo de mascota", ["Perro", "Gato", "Ave", "Otro"]) 

    with col2:
        st.subheader("Datos del Dueño")
        nombre_dueno = st.text_input("Nombre completo del dueño")
        numero_telefonico = st.text_input("Número de teléfono")

    st.subheader("Información Adicional")
    direccion = st.text_area("Dirección completa")
    notas = st.text_area("Notas adicionales (vacunas, alergias, etc.)")

    submit_button = st.form_submit_button(label="Enviar Registro")

    if submit_button:
        # Validación de campos requeridos
        if not nombre_mascota or not nombre_dueno or not numero_telefonico:
            st.error("Por favor completa todos los campos requeridos")
        elif not re.fullmatch(r"\+?\d{7,15}", numero_telefonico):
            st.error("Número de teléfono no válido. Usa solo dígitos y opcionalmente un +.")
        else:
            # Guardar datos en session state
            st.session_state.form_submitted = True
            st.session_state.form_data = {
                "nombre_mascota": nombre_mascota,
                "tipo_mascota": tipo_mascota,
                "nombre_dueno": nombre_dueno,
                "numero_telefonico": numero_telefonico,
                "direccion": direccion if direccion else "No especificada",
                "notas": notas if notas else "N/A"
            }
            st.rerun()

# Mostrar resultados fuera del formulario (evita conflictos de renderizado)
if st.session_state.form_submitted:
    data = st.session_state.form_data
    
    st.success("¡Registro completado exitosamente!")
    st.info(f"""
**Resumen del Registro:**
- **Mascota:** {data['nombre_mascota']} ({data['tipo_mascota']})
- **Dueño:** {data['nombre_dueno']}
- **Teléfono:** {data['numero_telefonico']}
- **Dirección:** {data['direccion']}
""")
    
    # Generar datos para el QR
    qr_data = f"""REGISTRO DE MASCOTA
Mascota: {data['nombre_mascota']}
Tipo: {data['tipo_mascota']}
Dueño: {data['nombre_dueno']}
Teléfono: {data['numero_telefonico']}
Dirección: {data['direccion']}
Notas: {data['notas']}"""
    
    # Verificamos que las librerías estén disponibles
    if not QR_LIB_AVAILABLE:
        st.error("La librería 'qrcode' o 'Pillow' no está disponible en este entorno.\nInstala las dependencias con: pip install qrcode[pil] Pillow\nSi estás desplegando en Streamlit Cloud, añade un archivo requirements.txt con estas líneas:\n\nstreamlit\nqrcode[pil]\nPillow\n")
    else:
        try:
            # Usamos la forma simple: qrcode.make devuelve una imagen PIL
            img = qrcode.make(qr_data)

            # Asegurarnos de que sea una imagen PIL.Image
            try:
                from PIL import Image as _PilCheck
                if not isinstance(img, _PilCheck.Image):
                    # Algunos wrappers pueden devolver objetos distintos; intentar obtener la imagen
                    try:
                        img = img.get_image()
                    except Exception:
                        pass
            except Exception:
                # Si por alguna razón Pillow no está disponible aquí, capturamos y seguimos
                pass

            # Mostrar el QR
            st.subheader("Código QR del Registro")
            st.image(img, caption="Escanea este código para ver los datos del registro", width=300)

            # Preparar descarga
            buffer = BytesIO()
            # Normalizar nombre de archivo (evitar caracteres problemáticos)
            safe_name = re.sub(r"[^0-9A-Za-z\-_.]", "_", data['nombre_mascota']) or "mascota"
            # Guardar imagen en buffer
            img.save(buffer, format="PNG")
            buffer.seek(0)

            st.download_button(
                label="Descargar código QR",
                data=buffer.getvalue(),
                file_name=f"qr_mascota_{safe_name}.png",
                mime="image/png"
            )

            # Botón para limpiar y nuevo registro
            if st.button("Nuevo Registro"):
                st.session_state.form_submitted = False
                st.session_state.form_data = {}
                st.rerun()
                
        except Exception as e:
            st.error(f"Error al generar el código QR: {e}")
