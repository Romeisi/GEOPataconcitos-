import streamlit as st
import json
import os
import base64
import math
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from datetime import date
import pandas as pd
import plotly.express as px

try:
    import psycopg2
except Exception:
    psycopg2 = None
import requests

st.set_page_config(
    page_title="GEOPataconcitos — Inteligencia Territorial",
    layout="wide",
    initial_sidebar_state="expanded",
)

PALETTE = {
    "bg":       "#E7F2E4",
    "bg2":      "#F4F1E2",
    "panel":    "#FFFFFF",
    "forest":   "#064E3B",
    "emerald":  "#059669",
    "teal":     "#0D9488",
    "lime":     "#4D7C0F",
    "lime_br":  "#84CC16",
    "amber":    "#D97706",
    "hazard":   "#E11D48",
    "sky":      "#0EA5E9",
    "ink":      "#0F2417",
    "ink_soft": "#3F5546",
    "line":     "#CFE0C8",
}
PX_COLORS = ["#059669", "#0D9488", "#84CC16", "#D97706", "#0EA5E9", "#7C3AED", "#E11D48", "#CA8A04"]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Space Grotesk', sans-serif;
    color: {PALETTE['ink']};
    font-size: 17px;
}}
.stApp {{
    background:
      radial-gradient(1200px 600px at 100% -5%, rgba(13,148,136,0.14), transparent 60%),
      radial-gradient(1000px 500px at -10% 10%, rgba(132,204,22,0.16), transparent 55%),
      linear-gradient(160deg, {PALETTE['bg']} 0%, {PALETTE['bg2']} 100%);
    background-attachment: fixed;
}}
#MainMenu, header[data-testid="stHeader"] {{ background: transparent; }}
footer {{ visibility: hidden; }}
.block-container {{ padding-top: 2.2rem; max-width: 1360px; }}

h1, h2, h3, h4 {{ font-family: 'Bricolage Grotesque', sans-serif !important; letter-spacing: -0.01em; color: {PALETTE['forest']}; }}

.block-container [data-testid="stMarkdownContainer"] p:not([class]),
.block-container [data-testid="stMarkdownContainer"] li:not([class]),
.block-container [data-testid="stMarkdownContainer"] strong:not([class]) {{ color: {PALETTE['ink']} !important; }}
.block-container [data-testid="stWidgetLabel"] * {{ color: {PALETTE['ink']} !important; }}

div[data-baseweb="tab-list"] {{ gap: 6px; border-bottom: 2px solid {PALETTE['line']}; }}
button[data-baseweb="tab"] {{ background: transparent !important; }}
button[data-baseweb="tab"], button[data-baseweb="tab"] p, button[data-baseweb="tab"] div, button[data-baseweb="tab"] span {{ color: #0FB5A9 !important; font-size: 18px !important; font-weight: 700 !important; }}
button[data-baseweb="tab"]:hover p {{ color: #0A8F86 !important; }}
button[data-baseweb="tab"][aria-selected="true"] p, button[data-baseweb="tab"][aria-selected="true"] span {{ color: {PALETTE['emerald']} !important; }}
div[data-baseweb="tab-highlight"] {{ background-color: #0FB5A9 !important; height: 4px !important; border-radius: 4px; }}

.gp-header {{
    background: linear-gradient(120deg, {PALETTE['forest']} 0%, {PALETTE['emerald']} 45%, {PALETTE['teal']} 78%, {PALETTE['lime']} 100%);
    border-radius: 18px;
    padding: 38px 42px;
    margin-bottom: 24px;
    box-shadow: 0 18px 48px rgba(6,78,59,0.30);
    position: relative; overflow: hidden;
}}
.gp-header::after {{
    content: ""; position: absolute; right: -60px; top: -60px; width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(132,204,22,0.55), transparent 70%);
}}
.gp-eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px; letter-spacing: 0.24em; text-transform: uppercase;
    color: {PALETTE['lime_br']}; margin: 0 0 10px 0;
}}
.gp-title {{
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 56px; font-weight: 800; color: #F5FBEF; margin: 0 0 8px 0;
    letter-spacing: -0.03em; line-height: 1.0;
}}
.gp-subtitle {{ font-size: 17.5px; color: #DCF1D6; margin: 0; max-width: 780px; line-height: 1.6; }}

.gp-kpi-box {{
    background: {PALETTE['panel']};
    border: 1px solid {PALETTE['line']};
    border-radius: 16px; padding: 20px 22px; text-align: left;
    box-shadow: 0 6px 18px rgba(6,78,59,0.08);
    border-left: 6px solid {PALETTE['emerald']};
    transition: transform .16s ease, box-shadow .16s ease;
}}
.gp-kpi-box:hover {{ transform: translateY(-4px); box-shadow: 0 14px 30px rgba(6,78,59,0.16); }}
.gp-kpi-val {{ font-family: 'Bricolage Grotesque', sans-serif; font-size: 44px; font-weight: 800; margin: 0; line-height: 1; }}
.gp-kpi-lbl {{ font-size: 14px; text-transform: uppercase; letter-spacing: 0.06em; color: {PALETTE['ink_soft']}; margin-top: 10px; font-weight: 600; }}
.k-emerald {{ border-left-color: {PALETTE['emerald']}; }} .k-emerald .gp-kpi-val {{ color: {PALETTE['emerald']}; }}
.k-hazard  {{ border-left-color: {PALETTE['hazard']};  }} .k-hazard  .gp-kpi-val {{ color: {PALETTE['hazard']}; }}
.k-amber   {{ border-left-color: {PALETTE['amber']};   }} .k-amber   .gp-kpi-val {{ color: {PALETTE['amber']}; }}
.k-teal    {{ border-left-color: {PALETTE['teal']};    }} .k-teal    .gp-kpi-val {{ color: {PALETTE['teal']}; }}

.gp-section {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 14px; letter-spacing: 0.16em; text-transform: uppercase;
    color: {PALETTE['teal']}; margin: 12px 0 8px 0;
    display: flex; align-items: center; gap: 14px;
}}
.gp-section::after {{ content: ""; flex: 1; height: 3px; border-radius: 3px;
    background: linear-gradient(90deg, {PALETTE['lime_br']}, transparent); }}

.gp-chart-card {{
    background: {PALETTE['panel']};
    border: 1px solid {PALETTE['line']};
    border-top: 5px solid {PALETTE['lime_br']};
    border-radius: 16px; padding: 22px 26px 10px 26px; margin-bottom: 10px;
    box-shadow: 0 6px 18px rgba(6,78,59,0.08);
}}
.gp-chart-title {{ font-family: 'Bricolage Grotesque', sans-serif; font-size: 24px; font-weight: 700; color: {PALETTE['forest']}; margin: 0 0 4px 0; }}
.gp-chart-desc {{ font-size: 15px; color: {PALETTE['ink_soft']}; margin: 0 0 12px 0; line-height: 1.55; }}

.gp-card {{
    background: {PALETTE['panel']};
    border: 1px solid {PALETTE['line']};
    border-left: 5px solid {PALETTE['teal']};
    border-radius: 14px; padding: 20px 24px; margin-bottom: 18px;
}}
.gp-card h4 {{ font-family: 'IBM Plex Mono', monospace; font-size: 13px; letter-spacing: 0.12em; text-transform: uppercase; color: {PALETTE['emerald']}; margin: 0 0 10px 0; }}
.gp-card p {{ font-size: 15.5px; line-height: 1.6; color: {PALETTE['ink_soft']}; margin: 0; }}

.gp-photo {{ border: 1px solid {PALETTE['line']}; border-radius: 16px; overflow: hidden; box-shadow: 0 6px 18px rgba(6,78,59,0.10); }}
.gp-photo img {{ display:block; width:100%; height:210px; object-fit:cover; opacity:0.88; filter:saturate(0.96); transition:opacity .2s ease, transform .25s ease; }}
.gp-photo:hover img {{ opacity:1; transform:scale(1.02); }}

section[data-testid="stSidebar"] {{ background: linear-gradient(200deg, {PALETTE['forest']} 0%, #0A3F30 100%); }}
section[data-testid="stSidebar"] * {{ color: #E8F5E2 !important; }}
.gp-side-title {{ font-family: 'Bricolage Grotesque', sans-serif; font-size: 32px; font-weight: 800; letter-spacing: -0.02em; color: #F5FBEF !important; margin: 6px 0 2px 0; }}
.gp-side-tag {{ font-family: 'IBM Plex Mono', monospace; font-size: 11.5px; color: {PALETTE['lime_br']} !important; letter-spacing: 0.12em; margin-bottom: 22px; }}
.gp-stat-row {{ display: flex; justify-content: space-between; align-items: baseline; padding: 11px 0; border-bottom: 1px solid rgba(255,255,255,0.10); }}
.gp-stat-label {{ font-size: 13px; letter-spacing: 0.03em; color: #B7D6AC !important; }}
.gp-stat-value {{ font-family: 'IBM Plex Mono', monospace; font-size: 15px; font-weight: 600; color: #F5FBEF !important; text-align: right; }}

.stButton>button, .stDownloadButton>button, div[data-testid="stFormSubmitButton"]>button {{
    font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 16px;
    background: linear-gradient(120deg, {PALETTE['emerald']}, {PALETTE['teal']}); color: #F5FBEF;
    border: none; border-radius: 12px; padding: 11px 22px;
    box-shadow: 0 6px 16px rgba(5,150,105,0.30);
}}
.stButton>button:hover, .stDownloadButton>button:hover, div[data-testid="stFormSubmitButton"]>button:hover {{
    background: linear-gradient(120deg, {PALETTE['forest']}, {PALETTE['emerald']}); color: #fff;
}}
</style>
""", unsafe_allow_html=True)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def categoria_desde_folder(folder: str) -> str:
    folder = folder or ""
    if "Puntos Críticos 2" in folder or "Puntos Criticos 2" in folder:
        return "Puntos Críticos 2"
    return "Puntos Críticos"


def _buscar_geojson():
    aqui = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.getenv("SEED_GEOJSON_PATH", ""),
        os.path.join(aqui, "patacones_coordenadas.geojson"),
        os.path.join(aqui, "..", "pipeline", "data", "patacones_coordenadas.geojson"),
        "patacones_coordenadas.geojson",
    ]
    for c in candidatos:
        if c and os.path.exists(c):
            return c
    return None


@st.cache_data(ttl=300)
def cargar_datos_seguros():
    try:
        r = requests.get(f"{API_BASE_URL}/locations", timeout=5)
        if r.status_code == 200 and r.json():
            return pd.DataFrame(r.json()), "API FastAPI (capa de exposición)"
    except Exception:
        pass

    if psycopg2 is not None:
        db_params = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "database": os.getenv("POSTGRES_DB", "monitoreo_ambiental"),
            "user": os.getenv("POSTGRES_USER", "romeisi"),
            "password": os.getenv("POSTGRES_PASSWORD", "ola123"),
            "port": os.getenv("POSTGRES_PORT", "5432"),
        }
        try:
            conn = psycopg2.connect(**db_params)
            df = pd.read_sql(
                "SELECT object_id, name, categoria, lon, lat FROM v_vertederos_consumo;", conn)
            conn.close()
            if not df.empty:
                return df, "PostgreSQL + PostGIS (directo)"
        except Exception:
            pass

    ruta = _buscar_geojson()
    if ruta:
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                gj = json.load(f)
            puntos = []
            for feat in gj.get("features", []):
                geom = feat.get("geometry", {}) or {}
                prop = feat.get("properties", {}) or {}
                if geom.get("type") != "Point":
                    continue
                lon, lat = geom.get("coordinates")
                oid = prop.get("OBJECTID") or prop.get("codigo_unico") or len(puntos) + 1
                puntos.append({
                    "object_id": prop.get("codigo_unico") or f"PAT-{int(oid):05d}",
                    "name": (prop.get("Name") or prop.get("name") or "Punto Crítico"),
                    "categoria": categoria_desde_folder(prop.get("FolderPath", "")),
                    "lon": lon, "lat": lat,
                })
            return pd.DataFrame(puntos), "Archivo GeoJSON local (261 puntos)"
        except Exception as err:
            return pd.DataFrame(), f"Error leyendo GeoJSON: {err}"
    return pd.DataFrame(), "Sin fuente de datos disponible"


def asignar_zona(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        df["zona"] = []
        return df
    clat, clon = df["lat"].mean(), df["lon"].mean()
    sectores = ["Norte", "Noreste", "Este", "Sureste", "Sur", "Suroeste", "Oeste", "Noroeste"]

    def zona(row):
        ang = math.degrees(math.atan2(row["lat"] - clat, row["lon"] - clon))
        idx = int(((90 - ang) % 360) / 45 + 0.5) % 8
        return sectores[idx]

    df = df.copy()
    df["zona"] = df.apply(zona, axis=1)
    return df


def _context_images():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    out = []
    for stem in ("contexto_1", "contexto_2"):
        for ext in (".jpg", ".jpeg", ".png"):
            p = os.path.join(base, stem + ext)
            if os.path.exists(p):
                mime = "png" if ext == ".png" else "jpeg"
                out.append((p, mime))
                break
    return out


df_patacones, fuente_datos = cargar_datos_seguros()
df_patacones = asignar_zona(df_patacones)

with st.sidebar:
    st.markdown('<div class="gp-side-title">GEOPataconcitos</div>', unsafe_allow_html=True)
    st.markdown('<div class="gp-side-tag">SISTEMA INTEGRADO DE MONITOREO</div>', unsafe_allow_html=True)

    if not df_patacones.empty:
        n_c1 = int((df_patacones["categoria"] == "Puntos Críticos").sum())
        n_c2 = int((df_patacones["categoria"] == "Puntos Críticos 2").sum())
        st.markdown(f"""
        <div class="gp-stat-row"><span class="gp-stat-label">PUNTOS CARGADOS</span><span class="gp-stat-value">{len(df_patacones):03d}</span></div>
        <div class="gp-stat-row"><span class="gp-stat-label">PUNTOS CRÍTICOS</span><span class="gp-stat-value">{n_c1:03d}</span></div>
        <div class="gp-stat-row"><span class="gp-stat-label">PUNTOS CRÍTICOS 2</span><span class="gp-stat-value">{n_c2:03d}</span></div>
        <div class="gp-stat-row"><span class="gp-stat-label">DISTRITO</span><span class="gp-stat-value">San Miguelito</span></div>
        <div class="gp-stat-row"><span class="gp-stat-label">ORIGEN DE DATOS</span><span class="gp-stat-value" style="font-size: 12px; color: {PALETTE['lime_br']} !important;">{fuente_datos}</span></div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top: 34px; font-size: 13.5px; line-height: 1.7; color: #B7D6AC !important; border-top: 1px solid rgba(255,255,255,0.16); padding-top: 18px;">
        <b>Proyecto del curso</b><br>Tópicos Especiales II · 2026<br>
        Desarrollado por:<br>
        <b>Romeisi Paniagua &amp; Paula Ramos</b><br>San Miguelito, Panamá
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="gp-header">
    <p class="gp-eyebrow">Dirección de Gestión Ambiental · Distrito de San Miguelito</p>
    <h1 class="gp-title">GEOPataconcitos</h1>
    <p class="gp-subtitle">
        Portal interactivo para el análisis georreferenciado e inventario de botaderos
        informales de basura del distrito. Explora el mapa satelital, la analítica territorial
        y registra nuevos focos en tiempo real.
    </p>
</div>
""", unsafe_allow_html=True)

tab_mapa, tab_tabla, tab_form = st.tabs([
    "Mapa de Monitoreo", "Registro de Datos", "Registrar Patacón",
])

CATEGORIAS = ["Puntos Críticos", "Puntos Críticos 2"]

with tab_mapa:
    if df_patacones.empty:
        st.warning("No hay datos disponibles. Verifica la conexión a la base o el archivo GeoJSON.")
    else:
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f"<div class='gp-kpi-box k-emerald'><p class='gp-kpi-val'>{len(df_patacones)}</p><p class='gp-kpi-lbl'>Total Pataconcitos</p></div>", unsafe_allow_html=True)
        with k2:
            st.markdown(f"<div class='gp-kpi-box k-hazard'><p class='gp-kpi-val'>{int((df_patacones['categoria']=='Puntos Críticos').sum())}</p><p class='gp-kpi-lbl'>Puntos Críticos</p></div>", unsafe_allow_html=True)
        with k3:
            st.markdown(f"<div class='gp-kpi-box k-amber'><p class='gp-kpi-val'>{int((df_patacones['categoria']=='Puntos Críticos 2').sum())}</p><p class='gp-kpi-lbl'>Puntos Críticos 2</p></div>", unsafe_allow_html=True)
        with k4:
            st.markdown(f"<div class='gp-kpi-box k-teal'><p class='gp-kpi-val'>{df_patacones['zona'].nunique()}</p><p class='gp-kpi-lbl'>Zonas con focos</p></div>", unsafe_allow_html=True)

        st.write("")
        st.markdown('<div class="gp-section">Mapa satelital de monitoreo</div>', unsafe_allow_html=True)

        col_m1, col_m2 = st.columns([3, 1])
        with col_m2:
            st.markdown("""<div class="gp-card"><h4>Filtro de Visualización</h4>
            <p>Cambia el fondo satelital con los controles del mapa. Al alejar el zoom, los puntos se agrupan en clústeres dinámicos.</p></div>""", unsafe_allow_html=True)
            SECTORES = ["Norte", "Noreste", "Este", "Sureste", "Sur", "Suroeste", "Oeste", "Noroeste"]
            zona_sel = st.selectbox("Filtrar por sector", ["Todos"] + SECTORES)
            st.markdown(f"<div style='margin-top:16px;font-size:15px;color:{PALETTE['ink_soft']};line-height:1.6;'>Haz clic en cualquier marcador para ver el código, el nombre oficial y la categoría del patacón.</div>", unsafe_allow_html=True)

        with col_m1:
            df_mapa = df_patacones.copy()
            if zona_sel != "Todos":
                df_mapa = df_mapa[df_mapa["zona"] == zona_sel]
            if df_mapa.empty:
                df_mapa = df_patacones.copy()

            centro = [df_mapa["lat"].mean(), df_mapa["lon"].mean()]
            mapa = folium.Map(location=centro, zoom_start=14, tiles=None, control_scale=True)
            folium.TileLayer(tiles="CartoDB positron", name="Mapa de Calles",
                             max_zoom=20, control=True).add_to(mapa)
            folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
                             attr="Google", name="Google Satélite (Earth)",
                             max_zoom=21, max_native_zoom=21, control=True).add_to(mapa)
            folium.TileLayer(tiles="https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/default/GoogleMapsCompatible/{z}/{y}/{x}.jpg",
                             attr="Sentinel-2 cloudless (EOX)", name="Sentinel-2 (Copernicus)",
                             max_zoom=16, max_native_zoom=16, control=True).add_to(mapa)

            cluster = MarkerCluster(name="Patacones").add_to(mapa)
            for _, row in df_mapa.iterrows():
                display_id = str(row["object_id"])
                color = PALETTE["hazard"] if row["categoria"] == "Puntos Críticos" else PALETTE["amber"]
                html_popup = f"""
                <div style="font-family:'Space Grotesk',sans-serif;min-width:190px;">
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;letter-spacing:0.05em;color:{color};margin-bottom:4px;">{display_id}</div>
                    <div style="font-size:15px;color:{PALETTE['forest']};font-weight:700;">{row['name']}</div>
                    <div style="font-size:12.5px;color:{PALETTE['ink_soft']};margin-top:5px;">Categoría: {row['categoria']}</div>
                    <div style="font-size:12.5px;color:{PALETTE['ink_soft']};">Distrito: San Miguelito</div>
                </div>"""
                icon_html = f"""<div style="width:14px;height:14px;background:{color};border:2px solid #F5FBEF;border-radius:50%;box-shadow:0 0 0 2px {PALETTE['emerald']};"></div>"""
                folium.Marker(location=[row["lat"], row["lon"]],
                              popup=folium.Popup(html_popup, max_width=260),
                              tooltip=f"{row['name']}",
                              icon=folium.DivIcon(html=icon_html, icon_size=(16, 16), icon_anchor=(8, 8))).add_to(cluster)
            folium.LayerControl(position="topright", collapsed=False).add_to(mapa)
            st_folium(mapa, height=560, use_container_width=True, returned_objects=[])

        st.write("")
        st.markdown('<div class="gp-section">Analítica territorial</div>', unsafe_allow_html=True)

        c1, c2 = st.columns([1.25, 1])
        with c1:
            st.markdown("""<div class="gp-chart-card">
                <p class="gp-chart-title">Jerarquía del problema — Treemap</p>
                <p class="gp-chart-desc">Cada bloque grande es una categoría operativa; dentro, cada foco específico. El tamaño refleja cuántos puntos concentra. Muestra la jerarquía de un vistazo.</p>""", unsafe_allow_html=True)
            df_tm = df_patacones.copy()
            df_tm["conteo"] = 1
            fig_tm = px.treemap(df_tm, path=[px.Constant("San Miguelito"), "categoria", "name"],
                                values="conteo", color="categoria", color_discrete_sequence=PX_COLORS)
            fig_tm.update_traces(root_color=PALETTE["bg"], marker=dict(line=dict(color="#FFFFFF", width=2)),
                                 hovertemplate="<b>%{label}</b><br>Focos: %{value}<extra></extra>")
            fig_tm.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=440,
                                 paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Space Grotesk", size=15, color=PALETTE["ink"]))
            st.plotly_chart(fig_tm, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("""<div class="gp-chart-card">
                <p class="gp-chart-title">Distribución por zona — Radar</p>
                <p class="gp-chart-desc">Cada vértice es una zona geográfica de San Miguelito (rosa de 8 sectores desde el centroide). La línea se estira según cuántos focos hay en esa dirección; un polígono deforme revela concentración territorial.</p>""", unsafe_allow_html=True)
            orden = ["Norte", "Noreste", "Este", "Sureste", "Sur", "Suroeste", "Oeste", "Noroeste"]
            df_z = (df_patacones.groupby("zona").size().reindex(orden, fill_value=0)
                    .reset_index(name="Cantidad"))
            fig_rad = px.line_polar(df_z, r="Cantidad", theta="zona", line_close=True)
            fig_rad.update_traces(fill="toself", fillcolor="rgba(5,150,105,0.28)",
                                  line=dict(color=PALETTE["emerald"], width=3),
                                  marker=dict(size=8, color=PALETTE["hazard"]))
            fig_rad.update_layout(margin=dict(l=50, r=50, t=30, b=30), height=440,
                                  paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Space Grotesk", size=13, color=PALETTE["ink"]),
                                  polar=dict(bgcolor="rgba(255,255,255,0.55)",
                                             radialaxis=dict(gridcolor=PALETTE["line"], showline=False)))
            st.plotly_chart(fig_rad, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""<div class="gp-chart-card">
            <p class="gp-chart-title">Mapa de calor de densidad — Hotspots</p>
            <p class="gp-chart-desc">Colorea de rojo intenso las zonas donde se agrupan muchos focos cercanos. No mide áreas: cuenta la concentración de puntos, como en epidemiología aplicada al monitoreo ambiental clandestino.</p>""", unsafe_allow_html=True)
        fig_hm = px.density_mapbox(df_patacones, lat="lat", lon="lon", radius=16,
                                   center=dict(lat=df_patacones["lat"].mean(), lon=df_patacones["lon"].mean()),
                                   zoom=11.5, mapbox_style="open-street-map",
                                   color_continuous_scale=["#064E3B", "#84CC16", "#F59E0B", "#E11D48"])
        fig_hm.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=520,
                             paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Space Grotesk", size=14, color=PALETTE["ink"]),
                             coloraxis_colorbar=dict(title="Densidad"))
        st.plotly_chart(fig_hm, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        _imgs = _context_images()
        if _imgs:
            st.write("")
            st.markdown('<div class="gp-section">Contexto del problema</div>', unsafe_allow_html=True)
            cols = st.columns(len(_imgs))
            for col, (p, mime) in zip(cols, _imgs):
                with col:
                    b64 = base64.b64encode(open(p, "rb").read()).decode()
                    st.markdown(f'<div class="gp-photo"><img src="data:image/{mime};base64,{b64}"/></div>', unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:13.5px;color:{PALETTE['ink_soft']};margin-top:8px;line-height:1.55;'>Registro visual de botaderos informales en vía pública: el fenómeno que este sistema inventaría, georreferencia y monitorea en San Miguelito.</p>", unsafe_allow_html=True)

with tab_tabla:
    if df_patacones.empty:
        st.warning("No hay registros para mostrar.")
    else:
        st.markdown("### Tabla de Atributos Geoespaciales")
        st.markdown("Refleja las columnas indexadas en PostgreSQL/PostGIS. Busca, filtra por categoría y descarga el reporte.")

        col_t1, col_t2 = st.columns([2, 1])
        with col_t2:
            filtro_cat = st.selectbox("Filtrar por categoría", ["Todas"] + CATEGORIAS, key="tabla_cat")
        with col_t1:
            busqueda = st.text_input("Buscar patacón por nombre")

        df_tabla = df_patacones.copy()
        if filtro_cat != "Todas":
            df_tabla = df_tabla[df_tabla["categoria"] == filtro_cat]
        if busqueda:
            df_tabla = df_tabla[df_tabla["name"].astype(str).str.contains(busqueda, case=False, na=False)]

        st.dataframe(
            df_tabla[["object_id", "name", "categoria", "zona", "lon", "lat"]],
            column_config={
                "object_id": "ID Registro", "name": "Nombre Oficial de Campo",
                "categoria": "Categoría", "zona": "Zona",
                "lon": "Longitud (WGS84)", "lat": "Latitud (WGS84)",
            },
            hide_index=True, use_container_width=True, height=520,
        )
        csv = df_tabla.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar Reporte (CSV)", data=csv,
                           file_name=f"reporte_pataconcitos_{date.today():%Y%m%d}.csv", mime="text/csv")

with tab_form:
    st.markdown("### Registrar un nuevo patacón")
    st.markdown("Da de alta un foco directamente en la base de datos monitoreo_ambiental. "
                "El registro queda disponible al instante para el mapa y la API.")

    colf, colg = st.columns([1.1, 1])
    with colf:
        with st.form("form_nuevo_pat", clear_on_submit=True):
            n_nombre = st.text_input("Nombre del foco *", placeholder="Ej. Antigua Piquera de Mano de Piedra")
            n_cat = st.selectbox("Categoría *", CATEGORIAS)
            cc1, cc2 = st.columns(2)
            with cc1:
                n_lat = st.number_input("Latitud *", value=9.0500, format="%.6f")
            with cc2:
                n_lon = st.number_input("Longitud *", value=-79.4900, format="%.6f")
            n_codigo = st.text_input("Código (opcional)", placeholder="Se autogenera: PAT-XXXXX")
            enviar = st.form_submit_button("Guardar en la base de datos")

        if enviar:
            if not n_nombre.strip():
                st.error("El nombre es obligatorio.")
            else:
                payload = {"nombre": n_nombre.strip(), "categoria": n_cat, "lat": n_lat, "lon": n_lon}
                if n_codigo.strip():
                    payload["codigo_unico"] = n_codigo.strip()
                try:
                    resp = requests.post(f"{API_BASE_URL}/locations", json=payload, timeout=8)
                    if resp.status_code == 201:
                        st.success(f"Patacón registrado correctamente: {resp.json()['object_id']}. "
                                   "Recarga la página para verlo en el mapa.")
                        st.cache_data.clear()
                    else:
                        st.error(f"No se pudo registrar ({resp.status_code}): {resp.json().get('detail', resp.text)}")
                except Exception as e:
                    st.error(f"La API no está disponible para el alta: {e}. "
                             "Levanta el servicio FastAPI (uvicorn api.main:app).")

    with colg:
        st.markdown("""<div class="gp-card"><h4>Cómo se ubican las coordenadas</h4>
        <p>Puedes obtener la latitud y longitud de un punto abriendo Google Maps, haciendo clic derecho
        sobre el sitio y copiando el par de coordenadas. San Miguelito está aproximadamente entre
        las latitudes 9.02 y 9.09 y las longitudes -79.52 y -79.45.</p></div>""", unsafe_allow_html=True)
        st.markdown("""<div class="gp-card"><h4>Flujo de datos</h4>
        <p>Al guardar, el dashboard envía un POST a la API FastAPI, que inserta el registro en
        PostGIS con su geometría POINT. Así se cierra el ciclo end-to-end: fuente, base, API y mapa.</p></div>""", unsafe_allow_html=True)
