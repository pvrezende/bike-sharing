import os
import pandas as pd
import psycopg2
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DB = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "bike_sharing"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}

# -----------------------------
# Visual / carousel layout
# -----------------------------
st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
    }
    [data-testid="stAppViewContainer"] > .main {
        overflow: hidden !important;
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { display: none; }
    [data-testid="stSidebar"] { display: none; }
    .block-container {
        padding: 1.0rem 2.0rem 0.8rem 2.0rem !important;
        max-width: 100% !important;
    }
    .dashboard-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: .45rem;
    }
    .dashboard-title {
        font-size: 1.75rem;
        font-weight: 800;
        letter-spacing: -.03em;
        margin: 0;
    }
    .dashboard-subtitle {
        color: #687385;
        font-size: .85rem;
        margin-top: .15rem;
    }
    .screen-label {
        text-align: center;
        color: #697386;
        font-size: .78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .09em;
        margin: .15rem 0 .45rem;
    }
    div.stButton > button {
        border-radius: 10px;
        min-height: 2.35rem;
        font-weight: 700;
    }
    .nav-current {
        text-align: center;
        font-weight: 800;
        padding: .55rem .2rem;
        border-radius: 10px;
        background: rgba(49, 51, 63, .08);
        margin: .05rem 0;
    }
    .kpi-card {
        border: 1px solid rgba(120,130,150,.18);
        border-radius: 14px;
        padding: .65rem .85rem;
        min-height: 90px;
        background: rgba(255,255,255,.55);
    }
    .kpi-name { color:#687385; font-size:.76rem; font-weight:700; }
    .kpi-value { font-size:1.45rem; font-weight:800; margin-top:.18rem; }
    .kpi-help { color:#8a94a6; font-size:.68rem; margin-top:.08rem; }
    .footer-note {
        text-align:center;
        color:#8a94a6;
        font-size:.68rem;
        margin-top:.35rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(ttl=30)
def query(sql):
    with psycopg2.connect(**DB) as conn:
        return pd.read_sql_query(sql, conn)


def money_int(value):
    return f"{int(value):,}".replace(",", ".")


def kpi_card(label, value, help_text=""):
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-name">{label}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart(fig, height=330):
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=55, b=35),
        font=dict(size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# -----------------------------
# Data
# -----------------------------
try:
    kpi = query("SELECT * FROM bike_indicadores WHERE id=1")
    if kpi.empty:
        st.warning("O banco está vazio. Execute: docker compose run --rm etl")
        st.stop()

    r = kpi.iloc[0]

    if "screen" not in st.session_state:
        st.session_state.screen = 0

    screens = [
        "Visão Geral",
        "Demanda por Hora",
        "Clima",
        "Usuários",
        "Período e Estação",
    ]

    # -----------------------------
    # Header
    # -----------------------------
    st.markdown(
        """
        <div class="dashboard-header">
          <div>
            <div class="dashboard-title">🚲 Bike Sharing</div>
            <div class="dashboard-subtitle">Análise de demanda • UCI Bike Sharing • ETL + PostgreSQL</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------
    # Horizontal navigation
    # -----------------------------
    nav = st.columns([0.8, 1.15, 1.15, 1.15, 1.15, 1.15, 0.8])
    if nav[0].button("◀", use_container_width=True, disabled=st.session_state.screen == 0):
        st.session_state.screen -= 1
        st.rerun()

    for i, name in enumerate(screens):
        if nav[i + 1].button(
            f"{i + 1}  {name}",
            use_container_width=True,
            type="primary" if i == st.session_state.screen else "secondary",
        ):
            st.session_state.screen = i
            st.rerun()

    if nav[6].button("▶", use_container_width=True, disabled=st.session_state.screen == len(screens) - 1):
        st.session_state.screen += 1
        st.rerun()

    st.markdown(
        f'<div class="screen-label">Tela {st.session_state.screen + 1} de {len(screens)} • {screens[st.session_state.screen]}</div>',
        unsafe_allow_html=True,
    )

    # -----------------------------
    # SCREEN 1 — Overview
    # -----------------------------
    if st.session_state.screen == 0:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            kpi_card("TOTAL DE LOCAÇÕES", money_int(r.total_locacoes), "período completo")
        with c2:
            kpi_card("MÉDIA POR HORA", f"{float(r.media_locacoes_hora):.2f}", "média dos registros")
        with c3:
            kpi_card("HORA DE PICO", f"{int(r.hora_pico):02d}:00", f"{money_int(r.locacoes_hora_pico)} locações")
        with c4:
            kpi_card("ALTA DEMANDA", f"{float(r.percentual_alta_demanda):.2f}%", "dos registros")

        by_hour = query("""
            SELECT hora, SUM(total_locacoes) AS locacoes
            FROM bike_sharing GROUP BY hora ORDER BY hora
        """)
        fig = px.area(by_hour, x="hora", y="locacoes", markers=True, title="Demanda total ao longo do dia")
        fig.update_xaxes(dtick=1, title="Hora")
        fig.update_yaxes(title="Locações")
        chart(fig, 390)

    # -----------------------------
    # SCREEN 2 — Hour
    # -----------------------------
    elif st.session_state.screen == 1:
        by_hour = query("""
            SELECT hora, SUM(total_locacoes) AS locacoes,
                   AVG(total_locacoes) AS media_registro
            FROM bike_sharing GROUP BY hora ORDER BY hora
        """)
        peak_row = by_hour.loc[by_hour["locacoes"].idxmax()]
        c1, c2, c3 = st.columns(3)
        with c1:
            kpi_card("PICO DO DIA", f"{int(peak_row.hora):02d}:00", "horário com maior demanda")
        with c2:
            kpi_card("LOCAÇÕES NO PICO", money_int(peak_row.locacoes), "total no horário")
        with c3:
            kpi_card("HORÁRIOS ANALISADOS", "24", "00h até 23h")

        fig = px.line(by_hour, x="hora", y="locacoes", markers=True, title="Demanda por hora do dia")
        fig.update_xaxes(dtick=1, title="Hora")
        fig.update_yaxes(title="Locações")
        chart(fig, 430)

    # -----------------------------
    # SCREEN 3 — Weather
    # -----------------------------
    elif st.session_state.screen == 2:
        weather = query("""
            SELECT descricao_clima, SUM(total_locacoes) AS locacoes,
                   AVG(temperatura_normalizada) AS temperatura,
                   AVG(umidade_normalizada) AS umidade
            FROM bike_sharing
            GROUP BY descricao_clima
            ORDER BY locacoes DESC
        """)
        top_weather = weather.iloc[0]
        c1, c2, c3 = st.columns(3)
        with c1:
            kpi_card("MELHOR CONDIÇÃO", str(top_weather.descricao_clima), "maior volume de locações")
        with c2:
            kpi_card("LOCAÇÕES", money_int(top_weather.locacoes), "na condição líder")
        with c3:
            kpi_card("CONDIÇÕES", str(len(weather)), "categorias no dataset")

        left, right = st.columns(2)
        with left:
            fig = px.bar(weather, x="descricao_clima", y="locacoes", title="Demanda por condição climática")
            fig.update_xaxes(title="Condição")
            fig.update_yaxes(title="Locações")
            chart(fig, 360)
        with right:
            climate_avg = weather.sort_values("locacoes", ascending=False)
            fig = px.bar(climate_avg, x="descricao_clima", y="temperatura", title="Temperatura normalizada média")
            fig.update_xaxes(title="Condição")
            fig.update_yaxes(title="Temperatura normalizada")
            chart(fig, 360)

    # -----------------------------
    # SCREEN 4 — Users
    # -----------------------------
    elif st.session_state.screen == 3:
        users = pd.DataFrame({
            "tipo": ["Casuais", "Registrados"],
            "usuarios": [int(r.usuarios_casuais), int(r.usuarios_registrados)],
        })
        total_users = users["usuarios"].sum()
        registered_pct = (int(r.usuarios_registrados) / total_users * 100) if total_users else 0

        c1, c2, c3 = st.columns(3)
        with c1:
            kpi_card("USUÁRIOS REGISTRADOS", money_int(r.usuarios_registrados), f"{registered_pct:.1f}% do total")
        with c2:
            kpi_card("USUÁRIOS CASUAIS", money_int(r.usuarios_casuais), f"{100 - registered_pct:.1f}% do total")
        with c3:
            kpi_card("TOTAL DE USUÁRIOS", money_int(total_users), "casuais + registrados")

        left, right = st.columns(2)
        with left:
            fig = px.pie(users, names="tipo", values="usuarios", hole=.48, title="Distribuição de usuários")
            chart(fig, 380)
        with right:
            users_long = pd.DataFrame({
                "categoria": ["Casuais", "Registrados"],
                "quantidade": [int(r.usuarios_casuais), int(r.usuarios_registrados)],
            })
            fig = px.bar(users_long, x="categoria", y="quantidade", text_auto=True, title="Comparação de usuários")
            fig.update_xaxes(title="Tipo")
            fig.update_yaxes(title="Usuários")
            chart(fig, 380)

    # -----------------------------
    # SCREEN 5 — Period / Season
    # -----------------------------
    else:
        period = query("""
            SELECT periodo_dia, SUM(total_locacoes) AS locacoes
            FROM bike_sharing GROUP BY periodo_dia ORDER BY locacoes DESC
        """)
        season = query("""
            SELECT descricao_estacao, SUM(total_locacoes) AS locacoes
            FROM bike_sharing GROUP BY descricao_estacao ORDER BY locacoes DESC
        """)
        best_period = period.iloc[0]
        best_season = season.iloc[0]

        c1, c2, c3 = st.columns(3)
        with c1:
            kpi_card("PERÍODO MAIS MOVIMENTADO", str(best_period.periodo_dia), "maior demanda")
        with c2:
            kpi_card("ESTAÇÃO MAIS MOVIMENTADA", str(best_season.descricao_estacao), "maior demanda")
        with c3:
            kpi_card("CATEGORIAS", f"{len(period)} + {len(season)}", "períodos + estações")

        left, right = st.columns(2)
        with left:
            fig = px.bar(period, x="periodo_dia", y="locacoes", title="Demanda por período do dia")
            fig.update_xaxes(title="Período")
            fig.update_yaxes(title="Locações")
            chart(fig, 365)
        with right:
            fig = px.bar(season, x="descricao_estacao", y="locacoes", title="Demanda por estação")
            fig.update_xaxes(title="Estação")
            fig.update_yaxes(title="Locações")
            chart(fig, 365)

    st.markdown(
        "<div class='footer-note'>Use os botões acima ou ◀ ▶ para navegar entre as telas • Dados atualizados do PostgreSQL</div>",
        unsafe_allow_html=True,
    )

except Exception as exc:
    st.error(f"Não foi possível consultar o banco: {exc}")
    st.info("Primeiro execute: docker compose run --rm etl")
