# Dashboard Power BI: Vacinas APS DF

Este diretório contém os artefatos para montar o dashboard no Power BI com o CSV disponível em `files/`.

## Importação

1. Abra o Power BI Desktop ou o Power BI Service.
2. Importe `files/dados_vacinas_aplicadas-24092026-anos_2026-meses_08.csv`.
3. No Power Query, use o conteúdo de `PowerQuery_Vacinas.pq` como referência para tipagem e tratamento.
4. Renomeie a tabela para `Vacinas`.
5. Crie as medidas de `Medidas_Vacinas.dax` na tabela `Vacinas`.

O arquivo tem 188.554 registros de doses, 27 campos, 35 imunobiológicos e competência agosto de 2026. O registro de 01/09 deve ser mantido para auditoria, mas filtrado nas páginas de competência quando necessário.

## Modelo recomendado

Use `Vacinas` como tabela fato. Para um relatório mais completo, crie uma tabela calendário:

```DAX
Calendario =
ADDCOLUMNS(
    CALENDAR(
        MIN('Vacinas'[i_dt_inicial_atendimento]),
        MAX('Vacinas'[i_dt_inicial_atendimento])
    ),
    "Ano", YEAR([Date]),
    "Mês", MONTH([Date]),
    "Mês/Ano", FORMAT([Date], "MM/yyyy"),
    "Dia da Semana", FORMAT([Date], "dddd")
)
```

Relacione `Calendario[Date]` com `Vacinas[i_dt_inicial_atendimento]` e marque `Calendario` como tabela de data.

## Páginas sugeridas

### 1. Visão executiva

- Cartões: Total de Doses, Estabelecimentos, RAs, Vacinas Distintas e Percentual Rotina.
- Linha: doses por dia.
- Barras: top 10 imunobiológicos.
- Barras empilhadas: doses por estratégia.
- Segmentadores: data, região de saúde, RA, vacina e faixa etária.

### 2. Perfil demográfico

- Doses por faixa etária.
- Distribuição por sexo.
- Doses menores de 5 anos e Doses 60 Mais.
- Matriz de vacina por faixa etária.

### 3. Território e operação

- Ranking de RAs.
- Ranking de regiões de saúde.
- Doses por local de atendimento.
- Doses por estabelecimento.
- Categoria profissional e CBO.

### 4. Qualidade e auditoria

- Registros Sem Região.
- Registros Fora da Competência.
- Doses Viajantes.
- Doses Comunicantes Hanseníase.
- Tabela de valores ausentes por coluna.

## Cuidados de interpretação

- O dataset registra doses, não pessoas únicas; volume não equivale a cobertura vacinal.
- Não há identificador de paciente nem denominador populacional.
- `i_gestante` e `i_puerpera` estão 100% ausentes neste arquivo.
- O pico de 22/08 deve ser tratado como possível backfill, não necessariamente como vacinação extraordinária.
- O CSV tem aproximadamente 58 MB. Para publicação recorrente, prefira armazená-lo em SharePoint, OneDrive, banco de dados ou dataflow em vez de depender de um caminho local.

## Entrega

O Power BI Desktop gera o arquivo `.pbix` localmente. Este repositório fornece os dados, a consulta, as medidas e o desenho do relatório para que o `.pbix` seja criado e publicado no workspace da equipe.