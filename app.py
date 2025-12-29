import streamlit as st
import sqlite3
from pdf import generar_boleta
import pandas as pd
from datetime import datetime
#---------------------------------------------------
if "vista" not in st.session_state:
    st.session_state.vista = None



with st.sidebar:
    st.title("Panel de Control")

    if st.button("👤 Registro de Cliente"):
        st.session_state.vista = "Registro de Cliente"
        st.rerun()

    if st.button("🧺 Registrar Servicio"):
        st.session_state.vista = "Registrar Servicio"
        st.rerun()

    if st.button("🧾 Crear Boleta"):
        st.session_state.vista = "Crear Boleta"
        st.rerun()

    if st.button("📂 Historial de Boletas"):
        st.session_state.vista = "Historial"
        st.rerun()

menu = st.session_state.vista

conn = sqlite3.connect("lavanderia.db", check_same_thread=False)

cursor = conn.cursor()
#---------------------------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS boletas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT,
    servicio TEXT,
    cantidad INTEGER,
    subtotal REAL,
    igv REAL,
    total REAL,
    fecha TEXT
)
""")
conn.commit()
#---------------------------------------------------


if "mostrar_form" not in st.session_state:
    st.session_state.mostrar_form = False

if "mostrar_form_servicio" not in st.session_state:
    st.session_state.mostrar_form_servicio = False
#---------------------------------------------------
if menu is None:
    st.markdown("""
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            height: 70vh;
            flex-direction: column;
            text-align: center;
        ">
            <h1>Bienvenido a Lavandería Mora</h1>
            <p>Seleccione una opción del panel para comenzar</p>
        </div>
    """, unsafe_allow_html=True)


#---------------------------------------------------
if menu == "Registro de Cliente":
    st.title("Sistema de Lavandería Mora")
    st.subheader("Clientes")

    clientes = cursor.execute("SELECT id, nombre, dni, telefono FROM clientes").fetchall()
    df = pd.DataFrame(clientes, columns=["ID", "Nombre", "DNI", "Teléfono"])

    df_editado = st.data_editor(df, num_rows="fixed", use_container_width=True)

    col1, col2 = st.columns([1,5])
    with col1:
        if st.button("➕ Nuevo Cliente"):
            st.session_state.mostrar_form = True

    if st.session_state.mostrar_form:
        with st.expander("Registrar nuevo cliente", expanded=True):

            nombre = st.text_input("Nombre")
            dni = st.text_input("DNI")
            telefono = st.text_input("Teléfono")

            colg1, colg2 = st.columns(2)
            with colg1:
                if st.button("Guardar"):
                    cursor.execute(
                        "INSERT INTO clientes (nombre, dni, telefono) VALUES (?, ?, ?)",
                        (nombre, dni, telefono)
                    )
                    conn.commit()
                    st.session_state.mostrar_form = False
                    st.rerun()

            with colg2:
                if st.button("Cancelar"):
                    st.session_state.mostrar_form = False
                    st.rerun()
    if st.button("Guardar Cambios"):
        for _, fila in df_editado.iterrows():
            cursor.execute("""
                UPDATE clientes
                SET nombre=?, dni=?, telefono=?
                WHERE id=?
            """, (fila["Nombre"], fila["DNI"], fila["Teléfono"], fila["ID"]))
        conn.commit()
        st.success("Cambios guardados")
#---------------------------------------------------

if menu == "Registrar Servicio":
    st.title("Sistema de Lavandería Mora")
    st.subheader("Servicios")

    servicios = cursor.execute("SELECT id, nombre, precio FROM servicios").fetchall()
    df = pd.DataFrame(servicios, columns=["ID", "Servicio", "Precio"])

    df_editado = st.data_editor(df, num_rows="fixed", use_container_width=True)

    col1, col2 = st.columns([1,5])
    with col1:
        if st.button("➕ Nuevo Servicio"):
            st.session_state.mostrar_form_servicio = True

    if st.session_state.mostrar_form_servicio:
        with st.expander("Registrar nuevo servicio", expanded=True):

            nombre = st.text_input("Nombre del servicio")
            precio = st.number_input("Precio", min_value=0.0)

            colg1, colg2 = st.columns(2)
            with colg1:
                if st.button("Guardar Servicio"):
                    cursor.execute(
                        "INSERT INTO servicios (nombre, precio) VALUES (?, ?)",
                        (nombre, precio)
                    )
                    conn.commit()
                    st.session_state.mostrar_form_servicio = False
                    st.rerun()

            with colg2:
                if st.button("Cancelar"):
                    st.session_state.mostrar_form_servicio = False
                    st.rerun()
    if st.button("Guardar Cambios de Servicios"):
        for _, fila in df_editado.iterrows():
            cursor.execute("""
                UPDATE servicios
                SET nombre=?, precio=?
                WHERE id=?
            """, (fila["Servicio"], fila["Precio"], fila["ID"]))
        conn.commit()
        st.success("Servicios actualizados")

#---------------------------------------------------
if menu == "Crear Boleta":
    st.title("Sistema de Lavandería Mora")
    st.subheader("Crear Boleta")

    clientes = cursor.execute("SELECT id, nombre FROM clientes").fetchall()
    cliente = st.selectbox("Cliente", clientes, format_func=lambda x: x[1])

    servicios = cursor.execute("SELECT * FROM servicios").fetchall()
    opcion = st.selectbox("Servicio", servicios, format_func=lambda x: f"{x[1]} - S/{x[2]}")

    cantidad = st.number_input("Cantidad", min_value=1, step=1)

    if st.button("Generar Boleta"):
        subtotal = opcion[2] * cantidad
        igv = subtotal * 0.18
        total = subtotal + igv

        # 1️⃣ Generar PDF
        ruta = generar_boleta(cliente[1], opcion[1], cantidad, subtotal, igv, total)

        # 2️⃣ Guardar en la base de datos (ESTA ES LA PARTE 2)
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO boletas (cliente, servicio, cantidad, subtotal, igv, total, fecha)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cliente[1], opcion[1], cantidad, subtotal, igv, total, fecha))
        conn.commit()

        # 3️⃣ Guardar ruta y confirmar
        st.session_state.ultima_boleta = ruta
        st.success("Boleta generada correctamente")

    if st.session_state.get("ultima_boleta"):
        with open(st.session_state.ultima_boleta, "rb") as f:
            st.download_button(
                "📄 Descargar Boleta PDF",
                f,
                file_name="boleta.pdf",
                mime="application/pdf"
            )
#---------------------------------------------------
if menu == "Historial":
    st.title("Historial de Boletas")

    boletas = cursor.execute("SELECT * FROM boletas ORDER BY fecha DESC").fetchall()

    df = pd.DataFrame(boletas, columns=["ID", "Cliente", "Servicio", "Cantidad", "Subtotal", "IGV", "Total", "Fecha"])

    st.dataframe(df, use_container_width=True)

    st.subheader("Reporte de Ventas")

    total_ventas = df["Total"].sum()
    total_igv = df["IGV"].sum()

    col1, col2 = st.columns(2)

    with col1:
        st.metric("💵 Total de Ventas", f"S/ {total_ventas:.2f}")

    with col2:
        st.metric("🧾 Total IGV", f"S/ {total_igv:.2f}")

#---------------------------------------------------
conn.close()
