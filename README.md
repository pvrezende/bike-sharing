# Trabalho Final — Módulo 6 Apache Hop

## Projeto escolhido
**Projeto 3 — Mobilidade Urbana e Bicicletas Compartilhadas**

Dataset oficial: **Bike Sharing Dataset — UCI Machine Learning Repository**.

Problema: **Em quais horários, dias e condições climáticas ocorre maior ou menor demanda por bicicletas?**

## Arquitetura
UCI Bike Sharing → ETL/tratamento → PostgreSQL → indicadores → Streamlit Dashboard

O projeto também inclui artefatos do Apache Hop na pasta `hop/` para a apresentação visual de pipelines/workflow e uma conexão PostgreSQL parametrizada.

## Requisitos na sua máquina
- Docker Desktop em execução
- PowerShell
- Internet na primeira execução (para baixar o dataset oficial da UCI)

Não é necessário instalar PostgreSQL nem Python.

## Execução rápida
Abra PowerShell na raiz do projeto e execute:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\start.ps1
```

Ou manualmente:

```powershell
docker compose up -d postgres dashboard
docker compose run --rm etl
docker compose ps
```

Depois abra:
- Dashboard: http://localhost:8501

### Apache Hop Web
O Hop Web é fornecido pelo projeto Apache Hop como opção web e pode variar por versão. Para tentar subir:

```powershell
docker compose --profile hop up -d hop-web
```

Depois teste:
- http://localhost:8080

A pasta do projeto está montada como `/files`.

## Testes pelo terminal

### Ver se os containers estão ativos
```powershell
docker compose ps
```

### Ver log do ETL
```powershell
docker compose run --rm etl
```

O final esperado é:
`[ETL] PROCESSO FINALIZADO COM SUCESSO.`

### Entrar no PostgreSQL
```powershell
docker exec -it bike_postgres psql -U postgres -d bike_sharing
```

Dentro do PostgreSQL:
```sql
SELECT COUNT(*) FROM bike_sharing;
SELECT * FROM bike_indicadores;
SELECT COUNT(*) - COUNT(DISTINCT instant) AS duplicados FROM bike_sharing;
```

Para sair:
```sql
\q
```

## Reprocessamento
A carga utiliza `instant` como chave primária e faz UPSERT (`ON CONFLICT ... DO UPDATE`).
Portanto, executar a carga novamente **não duplica os registros**: registros existentes são atualizados.

Teste:
```powershell
docker compose run --rm etl
docker compose run --rm etl
docker exec -it bike_postgres psql -U postgres -d bike_sharing -c "SELECT COUNT(*) AS total, COUNT(DISTINCT instant) AS unicos FROM bike_sharing;"
```

Os dois valores devem ser iguais.

## Transformações implementadas
- remoção de duplicidades por `instant`
- validação de colunas obrigatórias
- tratamento de nulos
- conversão de tipos
- conversão de data
- `periodo_dia`: MADRUGADA / MANHA / TARDE / NOITE
- `nivel_demanda`: BAIXA / MEDIA / ALTA (classificação analítica por tercis)
- descrição de clima
- descrição de estação do ano
- persistência PostgreSQL
- consolidação de indicadores
- validação de duplicidades

## Indicadores
1. total de locações
2. média de locações por registro/hora
3. hora com maior demanda
4. volume de locações na hora de pico
5. percentual de períodos em alta demanda
6. usuários casuais
7. usuários registrados
8. demanda por clima
9. demanda por período do dia
10. demanda por estação

## Estrutura
```text
apache-hop-bike-sharing/
├── database/
│   ├── init/01_schema.sql
│   └── consultas.sql
├── dataset/
├── etl/
├── dashboard/
├── hop/
│   ├── metadata/rdbms/bike_postgres.json
│   ├── pipelines/
│   └── workflows/
├── docs/
├── docker-compose.yml
├── start.ps1
└── reset.ps1
```

## Importante sobre os artefatos Hop
Os arquivos `.hpl` e `.hwf` foram organizados para representar visualmente o fluxo acadêmico e abrir no Apache Hop. A execução Docker de dados é independente e reproduz as regras documentadas, garantindo que o banco e o dashboard possam ser testados rapidamente. Antes da apresentação, valide a abertura desses arquivos na versão do Apache Hop disponibilizada pelo curso e, se a interface pedir atualização de metadados do formato, salve-os novamente no Hop GUI/Web.
