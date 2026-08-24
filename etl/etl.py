import io
import os
import time
import zipfile
from pathlib import Path

import pandas as pd
import psycopg2
import requests
from psycopg2.extras import execute_values

DATA_URL = os.getenv("DATA_URL")
DB = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "bike_sharing"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}

DATASET_DIR = Path("/app/dataset")
DATASET_DIR.mkdir(parents=True, exist_ok=True)
CSV_PATH = DATASET_DIR / "hour.csv"


def baixar_dataset():
    if CSV_PATH.exists():
        print(f"[ETL] Dataset já existe: {CSV_PATH}")
        return

    print(f"[ETL] Baixando dataset oficial da UCI...")
    r = requests.get(DATA_URL, timeout=120)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        candidates = [n for n in zf.namelist() if n.lower().endswith("hour.csv")]
        if not candidates:
            raise RuntimeError("hour.csv não encontrado dentro do ZIP da UCI.")
        with zf.open(candidates[0]) as src, open(CSV_PATH, "wb") as dst:
            dst.write(src.read())
    print(f"[ETL] Dataset salvo em {CSV_PATH}")


def transformar():
    print("[ETL] Lendo hour.csv...")
    df = pd.read_csv(CSV_PATH)

    # Validação e qualidade
    df = df.drop_duplicates(subset=["instant"]).copy()
    required = [
        "instant","dteday","season","yr","mnth","hr","holiday","weekday",
        "workingday","weathersit","temp","atemp","hum","windspeed",
        "casual","registered","cnt"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise RuntimeError(f"Colunas obrigatórias ausentes: {missing}")

    df = df.dropna(subset=required)
    df["data"] = pd.to_datetime(df["dteday"], errors="coerce").dt.date
    df = df.dropna(subset=["data"])

    numeric_cols = [c for c in required if c != "dteday"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=numeric_cols)

    # Campos derivados / regras analíticas do projeto
    def periodo(h):
        h = int(h)
        if 0 <= h <= 5: return "MADRUGADA"
        if 6 <= h <= 11: return "MANHA"
        if 12 <= h <= 17: return "TARDE"
        return "NOITE"

    q1 = float(df["cnt"].quantile(0.33))
    q2 = float(df["cnt"].quantile(0.66))

    def demanda(v):
        v = float(v)
        if v <= q1: return "BAIXA"
        if v <= q2: return "MEDIA"
        return "ALTA"

    clima = {
        1: "LIMPO_POUCAS_NUVENS",
        2: "NEVOA_NUBLADO",
        3: "CHUVA_NEVE_LEVE",
        4: "CONDICAO_SEVERA",
    }
    estacao = {1: "PRIMAVERA", 2: "VERAO", 3: "OUTONO", 4: "INVERNO"}

    out = pd.DataFrame({
        "instant": df["instant"].astype(int),
        "data": df["data"],
        "season": df["season"].astype(int),
        "ano": df["yr"].astype(int),
        "mes": df["mnth"].astype(int),
        "hora": df["hr"].astype(int),
        "feriado": df["holiday"].astype(int).astype(bool),
        "dia_semana": df["weekday"].astype(int),
        "dia_util": df["workingday"].astype(int).astype(bool),
        "clima": df["weathersit"].astype(int),
        "temperatura_normalizada": df["temp"].astype(float),
        "sensacao_termica_normalizada": df["atemp"].astype(float),
        "umidade_normalizada": df["hum"].astype(float),
        "vento_normalizado": df["windspeed"].astype(float),
        "usuarios_casuais": df["casual"].astype(int),
        "usuarios_registrados": df["registered"].astype(int),
        "total_locacoes": df["cnt"].astype(int),
        "periodo_dia": df["hr"].apply(periodo),
        "nivel_demanda": df["cnt"].apply(demanda),
        "descricao_clima": df["weathersit"].astype(int).map(clima).fillna("OUTRO"),
        "descricao_estacao": df["season"].astype(int).map(estacao).fillna("OUTRA"),
    })

    # Evidência de transformação para o relatório
    out.to_csv(DATASET_DIR / "hour_tratado.csv", index=False)
    print(f"[ETL] Registros tratados: {len(out):,}")
    print(f"[ETL] Limites analíticos de demanda: BAIXA <= {q1:.2f}; MEDIA <= {q2:.2f}; ALTA > {q2:.2f}")
    return out


def carregar(df):
    print("[ETL] Gravando dados tratados no PostgreSQL...")
    conn = psycopg2.connect(**DB)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            # Estratégia de reprocessamento: UPSERT pela chave instant.
            rows = list(df.itertuples(index=False, name=None))
            sql = """
                INSERT INTO bike_sharing (
                    instant,data,season,ano,mes,hora,feriado,dia_semana,dia_util,clima,
                    temperatura_normalizada,sensacao_termica_normalizada,umidade_normalizada,
                    vento_normalizado,usuarios_casuais,usuarios_registrados,total_locacoes,
                    periodo_dia,nivel_demanda,descricao_clima,descricao_estacao
                ) VALUES %s
                ON CONFLICT (instant) DO UPDATE SET
                    data=EXCLUDED.data,
                    season=EXCLUDED.season,
                    ano=EXCLUDED.ano,
                    mes=EXCLUDED.mes,
                    hora=EXCLUDED.hora,
                    feriado=EXCLUDED.feriado,
                    dia_semana=EXCLUDED.dia_semana,
                    dia_util=EXCLUDED.dia_util,
                    clima=EXCLUDED.clima,
                    temperatura_normalizada=EXCLUDED.temperatura_normalizada,
                    sensacao_termica_normalizada=EXCLUDED.sensacao_termica_normalizada,
                    umidade_normalizada=EXCLUDED.umidade_normalizada,
                    vento_normalizado=EXCLUDED.vento_normalizado,
                    usuarios_casuais=EXCLUDED.usuarios_casuais,
                    usuarios_registrados=EXCLUDED.usuarios_registrados,
                    total_locacoes=EXCLUDED.total_locacoes,
                    periodo_dia=EXCLUDED.periodo_dia,
                    nivel_demanda=EXCLUDED.nivel_demanda,
                    descricao_clima=EXCLUDED.descricao_clima,
                    descricao_estacao=EXCLUDED.descricao_estacao,
                    carga_em=CURRENT_TIMESTAMP
            """
            execute_values(cur, sql, rows, page_size=1000)

            # Consolidação de indicadores
            cur.execute("""
                INSERT INTO bike_indicadores (
                    id,total_locacoes,media_locacoes_hora,hora_pico,locacoes_hora_pico,
                    percentual_alta_demanda,usuarios_casuais,usuarios_registrados,atualizado_em
                )
                SELECT
                    1,
                    SUM(total_locacoes),
                    ROUND(AVG(total_locacoes)::numeric, 2),
                    (
                        SELECT hora FROM bike_sharing
                        GROUP BY hora ORDER BY SUM(total_locacoes) DESC LIMIT 1
                    ),
                    (
                        SELECT SUM(total_locacoes) FROM bike_sharing
                        GROUP BY hora ORDER BY SUM(total_locacoes) DESC LIMIT 1
                    ),
                    ROUND(100.0 * SUM(CASE WHEN nivel_demanda='ALTA' THEN 1 ELSE 0 END) / COUNT(*), 2),
                    SUM(usuarios_casuais),
                    SUM(usuarios_registrados),
                    CURRENT_TIMESTAMP
                FROM bike_sharing
                ON CONFLICT (id) DO UPDATE SET
                    total_locacoes=EXCLUDED.total_locacoes,
                    media_locacoes_hora=EXCLUDED.media_locacoes_hora,
                    hora_pico=EXCLUDED.hora_pico,
                    locacoes_hora_pico=EXCLUDED.locacoes_hora_pico,
                    percentual_alta_demanda=EXCLUDED.percentual_alta_demanda,
                    usuarios_casuais=EXCLUDED.usuarios_casuais,
                    usuarios_registrados=EXCLUDED.usuarios_registrados,
                    atualizado_em=CURRENT_TIMESTAMP
            """)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def validar():
    conn = psycopg2.connect(**DB)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*), COUNT(DISTINCT instant) FROM bike_sharing")
            total, unicos = cur.fetchone()
            cur.execute("SELECT total_locacoes, media_locacoes_hora, hora_pico, percentual_alta_demanda FROM bike_indicadores WHERE id=1")
            ind = cur.fetchone()
        print(f"[VALIDACAO] Linhas={total} | chaves únicas={unicos}")
        print(f"[VALIDACAO] Indicadores: total={ind[0]}, média={ind[1]}, hora_pico={ind[2]}, alta_demanda={ind[3]}%")
        if total != unicos:
            raise RuntimeError("Validação falhou: existem duplicidades.")
    finally:
        conn.close()


if __name__ == "__main__":
    baixar_dataset()
    df = transformar()
    carregar(df)
    validar()
    print("[ETL] PROCESSO FINALIZADO COM SUCESSO.")
