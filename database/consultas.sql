-- Verificar quantidade e duplicidades
SELECT COUNT(*) AS registros, COUNT(DISTINCT instant) AS chaves_unicas FROM bike_sharing;

-- KPIs
SELECT * FROM bike_indicadores;

-- Demanda por hora
SELECT hora, SUM(total_locacoes) AS locacoes
FROM bike_sharing GROUP BY hora ORDER BY hora;

-- Demanda por clima
SELECT descricao_clima, SUM(total_locacoes) AS locacoes
FROM bike_sharing GROUP BY descricao_clima ORDER BY locacoes DESC;

-- Demanda por estação
SELECT descricao_estacao, SUM(total_locacoes) AS locacoes
FROM bike_sharing GROUP BY descricao_estacao ORDER BY locacoes DESC;

-- Dias úteis x demais dias
SELECT dia_util, SUM(total_locacoes) AS locacoes
FROM bike_sharing GROUP BY dia_util;
