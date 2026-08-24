# Roteiro do Relatório — Trabalho Final Módulo 6

## 1. Identificação
Integrante(s): ______________________
Projeto escolhido: Projeto 3 — Mobilidade Urbana e Bicicletas Compartilhadas.

## 2. Dataset
Bike Sharing Dataset, UCI Machine Learning Repository.
Arquivo utilizado: `hour.csv`.

## 3. Problema
Em quais horários, dias e condições climáticas ocorre maior ou menor demanda por bicicletas?

## 4. Arquitetura
Dataset UCI → ingestão → tratamento → PostgreSQL → consolidação → indicadores → dashboard.

**PRINT 1:** estrutura das pastas / Docker funcionando.

## 5. Pipeline de ingestão e tratamento
Explique a leitura do CSV e as etapas de validação, conversão, enriquecimento e controle de duplicidade.

**PRINT 2:** pipeline `01_ingestao_tratamento_bike_sharing`.

## 6. Workflow
Workflow principal orquestra ingestão/tratamento e consolidação.

**PRINT 3:** `main_bike_sharing.hwf`.

## 7. Tratamentos
- tipos e data
- nulos
- duplicidades
- período do dia
- nível de demanda
- clima
- estação

Observação: BAIXA/MEDIA/ALTA é uma classificação analítica definida para este projeto com base em tercis do campo `cnt`.

## 8. Banco de dados
Tabela detalhada: `bike_sharing`.
Tabela resumida: `bike_indicadores`.
Chave primária: `instant`.

**PRINT 4:** terminal com `\dt`.
**PRINT 5:** `SELECT COUNT(*) ...`.

## 9. Indicadores
Apresente total, média, hora de pico, alta demanda, casuais x registrados e comparações climáticas/temporais.

## 10. Dashboard
**PRINT 6 e 7:** dashboard no navegador.

## 11. Validação
Compare `COUNT(*)` com `COUNT(DISTINCT instant)`.
Reexecute o ETL e demonstre que a contagem não aumenta por duplicação.

## 12. Conclusão
Descreva quais horários/condições apresentaram maior demanda após executar o dataset real. Não invente resultados: use os números exibidos no dashboard.
