import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

st.set_page_config(page_title="ESVD | Servicios ecosistémicos", layout="wide")
DATA_FILE = "ESVD_limpia_final_sin_multibioma.csv"

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    for col in ["latitude", "longitude", "int_per_hectare_per_year", "study_id"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Requisitos mínimos para tabla
    df = df.dropna(subset=["esvd2_0_biome", "esvd2_0_ecosystems", "es_1", "int_per_hectare_per_year", "study_id"])
    return df

df = load_data(DATA_FILE)

def safe_unique_sorted(series):
    return sorted(series.dropna().astype(str).unique().tolist())

def ensure_valid_selection(key: str, options: list, default=None):
    if key not in st.session_state:
        st.session_state[key] = default if default in options else (options[0] if options else None)
        return
    if st.session_state[key] not in options:
        st.session_state[key] = default if default in options else (options[0] if options else None)

# -----------------------------
# SIDEBAR: CASCADA (Bioma obligatorio)
# -----------------------------
st.sidebar.header("Filtros (cascada)")

# 1) BIOMA (obligatorio)
biome_options = safe_unique_sorted(df["esvd2_0_biome"])
ensure_valid_selection("biome_sel", biome_options, default=(biome_options[0] if biome_options else None))
biome_sel = st.sidebar.selectbox("1) Bioma", biome_options, key="biome_sel")

df_b = df[df["esvd2_0_biome"].astype(str) == str(biome_sel)].copy()
if df_b.empty:
    st.error("No hay datos para el bioma seleccionado.")
    st.stop()

# 2) ECOZONA (depende de Bioma) + (Todos)
ecozone_options = ["(Todos)"] + safe_unique_sorted(df_b["esvd2_0_ecozones"])
ensure_valid_selection("ecozone_sel", ecozone_options, default="(Todos)")
ecozone_sel = st.sidebar.selectbox("2) Ecozona", ecozone_options, key="ecozone_sel")

df_be = df_b.copy()
if ecozone_sel != "(Todos)":
    df_be = df_be[df_be["esvd2_0_ecozones"].astype(str) == str(ecozone_sel)]

if df_be.empty:
    st.error("No hay datos para la ecozona seleccionada dentro del bioma.")
    st.stop()

# 3) ECOSISTEMA (depende de Bioma + Ecozona) + (Todos)
ecosystem_options = ["(Todos)"] + safe_unique_sorted(df_be["esvd2_0_ecosystems"])
ensure_valid_selection("ecosystem_sel", ecosystem_options, default="(Todos)")
ecosystem_sel = st.sidebar.selectbox("3) Ecosistema", ecosystem_options, key="ecosystem_sel")

df_e = df_be.copy()
if ecosystem_sel != "(Todos)":
    df_e = df_e[df_e["esvd2_0_ecosystems"].astype(str) == str(ecosystem_sel)]

if df_e.empty:
    st.error("No hay registros con la combinación de filtros seleccionada.")
    st.stop()

# -----------------------------
# TABS
# -----------------------------
tab1, tab2 = st.tabs(["📊 Tabla (promedios)", "🗺️ Mapa (estudios)"])

# ============================================================
# TAB 1: Promedios por servicio usando TODAS las observaciones
# Conteo de investigaciones: study_id únicos
# ============================================================
with tab1:
    st.title("Promedios por servicio ecosistémico (todas las observaciones)")
    st.caption(
        "Promedios/medianas/rangos calculados sobre todas las filas. "
        "El conteo de investigaciones es por study_id único."
    )

    summary = (
        df_e.groupby("es_1", as_index=False)
        .agg(
            estudios_unicos=("study_id", "nunique"),                  # conteo por estudio único
            n_observaciones=("int_per_hectare_per_year", "count"),    # filas usadas (útil para transparencia)
            promedio_simple=("int_per_hectare_per_year", "mean"),
            mediana=("int_per_hectare_per_year", "median"),
            minimo=("int_per_hectare_per_year", "min"),
            maximo=("int_per_hectare_per_year", "max"),
        )
        .rename(columns={"es_1": "servicio_ecosistemico"})
        .sort_values("promedio_simple", ascending=False)
    )

    # TOTAL del subconjunto filtrado
    total_estudios = int(df_e["study_id"].nunique())
    total_obs = int(df_e["int_per_hectare_per_year"].count())

    suma_promedios = float(summary["promedio_simple"].sum())  # suma de promedios por servicio (como solicitaste)
    mediana_global = float(df_e["int_per_hectare_per_year"].median())
    min_global = float(df_e["int_per_hectare_per_year"].min())
    max_global = float(df_e["int_per_hectare_per_year"].max())

    total_row = pd.DataFrame([{
        "servicio_ecosistemico": "TOTAL (filtros actuales)",
        "estudios_unicos": total_estudios,
        "n_observaciones": total_obs,
        "promedio_simple": suma_promedios,
        "mediana": mediana_global,
        "minimo": min_global,
        "maximo": max_global
    }])

    out = pd.concat([summary, total_row], ignore_index=True)

    # Mostrar redondeado
    out_show = out.copy()
    for c in ["promedio_simple", "mediana", "minimo", "maximo"]:
        out_show[c] = out_show[c].astype(float).round(2)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Bioma", biome_sel)
    c2.metric("Ecozona", ecozone_sel)
    c3.metric("Ecosistema", ecosystem_sel)
    c4.metric("Estudios únicos (total)", total_estudios)

    st.dataframe(out_show, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Descargar tabla (CSV)",
        data=out.to_csv(index=False).encode("utf-8"),
        file_name=f"tabla_{biome_sel}_{ecozone_sel}_{ecosystem_sel}.csv".replace(" ", "_"),
        mime="text/csv",
    )

# ============================================================
# TAB 2: Mapa por estudio (según filtros en cascada)
# ============================================================
with tab2:
    st.title("Mapa de estudios (según filtros en cascada)")

    # Filtro adicional por servicio (solo mapa)
    service_options = ["(Todos)"] + safe_unique_sorted(df_e["es_1"])
    ensure_valid_selection("service_map_sel", service_options, default="(Todos)")
    service_sel = st.selectbox("Filtrar por servicio (mapa)", service_options, key="service_map_sel")

    df_map_base = df_e.copy()
    if service_sel != "(Todos)":
        df_map_base = df_map_base[df_map_base["es_1"].astype(str) == str(service_sel)]

    df_map_base = df_map_base.dropna(subset=["latitude", "longitude"])
    if df_map_base.empty:
        st.warning("No hay puntos con coordenadas para mostrar con los filtros actuales.")
        st.stop()

    def build_services_block(d: pd.DataFrame) -> str:
        rows = []
        for _, r in d.iterrows():
            rows.append(f"<li><b>{r['es_1']}</b>: {float(r['int_per_hectare_per_year']):.2f}</li>")
        return "<ul style='margin:0; padding-left:18px;'>" + "".join(rows) + "</ul>"

    grouped = []
    for sid, d in df_map_base.groupby("study_id"):
        d1 = d.iloc[0]
        services_html = build_services_block(d)

        metodo = d1.get("valuation_methods", "")
        if pd.isna(metodo):
            metodo = ""

        tooltip_html = f"""
        <div style="max-width: 380px;">
          <div><b>País:</b> {d1.get('countries','')}</div>
          <div><b>Ecosistema:</b> {d1.get('esvd2_0_ecosystems','')}</div>
          <div><b>Método:</b> {metodo}</div>
          <div style="margin-top:6px;"><b>Servicios y valores (USD/ha/año):</b></div>
          {services_html}
        </div>
        """

        grouped.append({
            "study_id": sid,
            "latitude": float(d1["latitude"]),
            "longitude": float(d1["longitude"]),
            "value_med": float(d["int_per_hectare_per_year"].median()),
            "tooltip_html": tooltip_html
        })

    df_points = pd.DataFrame(grouped)

    v = df_points["value_med"].astype(float)
    p5, p95 = np.nanpercentile(v, [5, 95])
    df_points["value_clip"] = np.clip(v, p5, p95)

    center_lat = float(df_points["latitude"].mean())
    center_lon = float(df_points["longitude"].mean())

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_points,
        get_position="[longitude, latitude]",
        get_radius="value_clip",
        radius_scale=25,
        radius_min_pixels=3,
        radius_max_pixels=60,
        get_fill_color="[50, 120, 200, 160]",
        pickable=True,
        auto_highlight=True,
    )

    deck = pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=2.5),
        layers=[layer],
        tooltip={"html": "{tooltip_html}", "style": {"backgroundColor": "white", "color": "black"}},
    )

    st.pydeck_chart(deck, use_container_width=True)
    st.caption(f"Puntos (estudios únicos) mostrados en el mapa: {len(df_points)}")
