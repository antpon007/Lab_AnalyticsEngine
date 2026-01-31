import streamlit as st
import pandas as pd
import time

# ======================================================
# CONFIGURACIÓN GENERAL
# ======================================================
st.set_page_config(
    page_title="Simulador Apache Cassandra",
    layout="wide"
)

st.title("🗄️ Simulador Apache Cassandra – Wide Column Store")
st.caption("Modelado por Column Families, consultas selectivas y analítica por columnas")

# ======================================================
# INICIALIZACIÓN DE COLUMN FAMILIES
# ======================================================
if "Datos_Usuario" not in st.session_state:
    st.session_state.Datos_Usuario = {}

if "Datos_Geograficos" not in st.session_state:
    st.session_state.Datos_Geograficos = {}

if "Datos_Metricas" not in st.session_state:
    st.session_state.Datos_Metricas = {}

usuarios = st.session_state.Datos_Usuario
geo = st.session_state.Datos_Geograficos
metricas = st.session_state.Datos_Metricas

familias = {
    "Datos_Usuario": usuarios,
    "Datos_Geograficos": geo,
    "Datos_Metricas": metricas
}

# ======================================================
# TABS
# ======================================================
tab_insert, tab_view, tab_query, tab_analytics = st.tabs(
    ["➕ Inserción", "📦 Column Families", "🔍 Consulta", "📊 Analítica"]
)

# ======================================================
# TAB 1 – INSERCIÓN
# ======================================================
with tab_insert:
    st.subheader("➕ Inserción simultánea en Column Families")

    with st.form("insert_form"):
        pk = st.text_input("Clave primaria (ID Usuario)")

        st.markdown("### 👤 Datos Usuario")
        nombre = st.text_input("Nombre")
        email = st.text_input("Email")

        st.markdown("### 🌍 Datos Geográficos")
        pais = st.text_input("País")
        ciudad = st.text_input("Ciudad")

        st.markdown("### 📊 Datos Métricas")
        visitas = st.number_input("Visitas", min_value=0, step=1)
        gasto_total = st.number_input("Gasto total", min_value=0.0, step=0.5)
        gasto_publicitario = st.number_input(
            "Gasto Publicitario", min_value=0.0, step=0.5
        )

        submitted = st.form_submit_button("Guardar registro")

        if submitted:
            if not pk:
                st.error("❌ La clave primaria es obligatoria")
            else:
                ts = int(time.time())

                usuarios[pk] = {
                    "nombre": nombre,
                    "email": email,
                    "ts": ts
                }

                geo[pk] = {
                    "pais": pais,
                    "ciudad": ciudad,
                    "ts": ts
                }

                metricas[pk] = {
                    "visitas": visitas,
                    "gasto_total": gasto_total,
                    "gasto_publicitario": gasto_publicitario,
                    "ts": ts
                }

                st.success("✅ Registro insertado en todas las Column Families")

# ======================================================
# TAB 2 – VISUALIZACIÓN DE COLUMN FAMILIES
# ======================================================
with tab_view:
    st.subheader("📦 Datos por Column Family")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### 👤 Datos_Usuario")
        st.dataframe(
            pd.DataFrame.from_dict(usuarios, orient="index")
            if usuarios else pd.DataFrame(),
            use_container_width=True
        )

    with c2:
        st.markdown("### 🌍 Datos_Geograficos")
        st.dataframe(
            pd.DataFrame.from_dict(geo, orient="index")
            if geo else pd.DataFrame(),
            use_container_width=True
        )

    with c3:
        st.markdown("### 📊 Datos_Metricas")
        st.dataframe(
            pd.DataFrame.from_dict(metricas, orient="index")
            if metricas else pd.DataFrame(),
            use_container_width=True
        )

# ======================================================
# TAB 3 – CONSULTA SELECTIVA
# ======================================================
with tab_query:
    st.subheader("🔍 Consulta selectiva por columnas")

    family_name = st.selectbox(
        "Selecciona la Column Family",
        list(familias.keys())
    )

    family_data = familias[family_name]

    if family_data:
        df_full = pd.DataFrame.from_dict(family_data, orient="index")
        columnas_disponibles = df_full.columns.tolist()

        columnas_seleccionadas = st.multiselect(
            "Columnas a leer",
            columnas_disponibles,
            default=columnas_disponibles
        )

        if st.button("Ejecutar consulta"):
            start = time.time()

            df_resultado = df_full[columnas_seleccionadas]

            elapsed_ms = (time.time() - start) * 1000
            columnas_ignoradas = (
                len(columnas_disponibles) - len(columnas_seleccionadas)
            )

            st.metric(
                "⏱️ Tiempo de procesamiento (ms)",
                f"{elapsed_ms:.2f}"
            )

            st.info(
                f"📉 Columnas ignoradas: {columnas_ignoradas} "
                "(ahorro de ancho de banda)"
            )

            st.dataframe(df_resultado, use_container_width=True)
    else:
        st.warning("⚠️ No hay datos en esta Column Family")

# ======================================================
# TAB 4 – ANALÍTICA POR COLUMNAS
# ======================================================
with tab_analytics:
    st.subheader("📊 Analítica por columnas (Wide-Column)")

    if geo and metricas:
        df_geo = pd.DataFrame.from_dict(geo, orient="index")
        df_metricas = pd.DataFrame.from_dict(metricas, orient="index")

        if "ciudad" in df_geo.columns and "gasto_publicitario" in df_metricas.columns:
            df_analitica = pd.DataFrame({
                "Ciudad": df_geo["ciudad"],
                "Gasto_Publicitario": df_metricas["gasto_publicitario"]
            })

            resultado = (
                df_analitica
                .groupby("Ciudad", as_index=True)
                .sum()
            )

            st.bar_chart(resultado)

            st.markdown("""
### ⚡ ¿Por qué esta operación es ultra rápida?

- Solo se escanean **2 columnas**: `Ciudad` y `Gasto_Publicitario`
- No se leen datos de usuario ni métricas innecesarias
- No existen joins relacionales
- El modelo wide-column está optimizado para este patrón

👉 En **Apache Cassandra**, este tipo de consulta escala a millones de registros
con baja latencia y mínimo uso de ancho de banda.
""")
        else:
            st.warning(
                "⚠️ Faltan columnas necesarias para la analítica "
                "(`ciudad`, `gasto_publicitario`)"
            )
    else:
        st.info("No hay datos suficientes para realizar la analítica.")

# ======================================================
# EXPLICACIÓN FINAL
# ======================================================
with st.expander("📘 Relación con Apache Cassandra"):
    st.markdown("""
- **Column Families independientes**
- **Clave primaria compartida**
- **Desnormalización controlada**
- **Lecturas selectivas por columna**
- **Analítica eficiente sin escanear toda la base**

Esta app simula los principios fundamentales de Apache Cassandra
y su ventaja frente a modelos relacionales tradicionales.
""")
