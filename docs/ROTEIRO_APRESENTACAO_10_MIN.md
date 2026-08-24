# Roteiro de apresentação — máximo 10 minutos

## 0:00–1:00 — Contexto
- Projeto 3: Bike Sharing.
- Dataset público UCI.
- Problema: identificar horários, dias e condições com maior/menor demanda.

## 1:00–4:00 — ETL / Apache Hop
- mostrar pipeline principal
- entrada CSV
- validação/conversão
- tratamento
- campos derivados
- duplicidades
- persistência
- mostrar workflow de orquestração

## 4:00–6:00 — PostgreSQL
- `docker compose ps`
- entrar com psql
- `\dt`
- explicar `bike_sharing` e `bike_indicadores`
- explicar chave `instant`

## 6:00–9:00 — Dashboard
- KPIs
- hora de pico
- clima
- casuais x registrados
- período do dia
- estação

## 9:00–10:00 — Conclusão e reprocessamento
- executar ETL novamente não duplica
- UPSERT por `instant`
- principal resultado obtido nos gráficos
- aprendizado: integração entre ETL, banco e visualização
