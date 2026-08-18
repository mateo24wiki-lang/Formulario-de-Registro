import streamlit as st
import re
import qrcode
from io import BytesIO

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
    
    try:
        # Crear el código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Generar imagen del QR
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Mostrar el QR
        st.subheader("Código QR del Registro")
        st.image(img, caption="Escanea este código para ver los datos del registro", width=300)
        
        # Opción para descargar el QR
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        st.download_button(
            label="Descargar código QR",
            data=buffer.getvalue(),
            file_name=f"qr_mascota_{data['nombre_mascota']}.png",
            mime="image/png"
        )
        
        # Botón para limpiar y nuevo registro
        if st.button("Nuevo Registro"):
            st.session_state.form_submitted = False
            st.session_state.form_data = {}
            st.rerun()
            
    except Exception as e:
        st.error(f"Error al generar el código QR: {e}")
