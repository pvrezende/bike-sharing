CREATE TABLE IF NOT EXISTS bike_sharing (
    instant INTEGER PRIMARY KEY,
    data DATE NOT NULL,
    season INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    hora INTEGER NOT NULL,
    feriado BOOLEAN NOT NULL,
    dia_semana INTEGER NOT NULL,
    dia_util BOOLEAN NOT NULL,
    clima INTEGER NOT NULL,
    temperatura_normalizada NUMERIC(8,5),
    sensacao_termica_normalizada NUMERIC(8,5),
    umidade_normalizada NUMERIC(8,5),
    vento_normalizado NUMERIC(8,5),
    usuarios_casuais INTEGER NOT NULL,
    usuarios_registrados INTEGER NOT NULL,
    total_locacoes INTEGER NOT NULL,
    periodo_dia VARCHAR(20) NOT NULL,
    nivel_demanda VARCHAR(20) NOT NULL,
    descricao_clima VARCHAR(80) NOT NULL,
    descricao_estacao VARCHAR(30) NOT NULL,
    carga_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bike_indicadores (
    id INTEGER PRIMARY KEY,
    total_locacoes BIGINT NOT NULL,
    media_locacoes_hora NUMERIC(14,2) NOT NULL,
    hora_pico INTEGER NOT NULL,
    locacoes_hora_pico BIGINT NOT NULL,
    percentual_alta_demanda NUMERIC(8,2) NOT NULL,
    usuarios_casuais BIGINT NOT NULL,
    usuarios_registrados BIGINT NOT NULL,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bike_data ON bike_sharing(data);
CREATE INDEX IF NOT EXISTS idx_bike_hora ON bike_sharing(hora);
CREATE INDEX IF NOT EXISTS idx_bike_clima ON bike_sharing(clima);
CREATE INDEX IF NOT EXISTS idx_bike_periodo ON bike_sharing(periodo_dia);
