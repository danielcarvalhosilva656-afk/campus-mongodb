# Atividade A12 - Consultas Avançadas no MongoDB (CampusFlow)

Da consulta operacional à informação para decisão.

## Estrutura
```
a12/
├── seed.py        # popula o banco (200 solicitações, reproduzível)
├── consultas.py   # 1 find() avançado + 3 pipelines + 1 indicador final
├── relatorio.py   # executa tudo e gera o relatório (relatorio.md)
└── README.md
```

## Como executar
```bash
pip install pymongo

python seed.py
python relatorio.py
```

## Modelo do documento
`protocolo`, `estudante{nome, matricula, curso}`, `categoria{nome}`, `situacao`,
`prioridade (1-5)`, `tags[]`, `criadoEm`, `atendimentos[{setor, duracaoMin, data}]`.

## Consultas

| # | Pergunta da coordenação | Técnica |
|---|---|---|
| find() | Quais casos devem ser atendidos primeiro? | filtro composto (`$in`, `$gte`, `$elemMatch`), projeção, `sort`, `limit` |
| Pipeline 1 | Quais categorias concentram mais casos? | `$match` -> `$group` (`$sum`, `$avg`, `$max`) -> `$project` -> `$sort` |
| Pipeline 2 | Qual setor recebe mais interações? | `$match` -> `$unwind` -> `$group` -> `$sort` |
| Pipeline 3 | Quais estudantes aparecem repetidamente? | `$group` -> `$match` (sobre o grupo) -> `$sort` -> `$limit` |
| Indicador final | Onde está o backlog crítico? | `$project` com `$cond` e `$sum` sobre array -> `$group` -> % crítico |

**Indicador operacional final - % de backlog crítico por categoria:**
`casos críticos (prioridade >= 4, em andamento) / backlog da categoria x 100`,
junto do esforço acumulado em minutos. Indica onde concentrar a equipe.

## Decisões técnicas
- **`$match` no início** dos pipelines: menos documentos atravessam os estágios seguintes.
- **Índice** `(situacao asc, prioridade desc)` criado no `seed.py`, compatível com o
  filtro de situação e a ordenação por prioridade.
- **`$unwind` muda a unidade de contagem**: no Pipeline 2, `$sum: 1` conta
  *atendimentos*, não solicitações. Por isso os Pipelines 1, 3 e o indicador
  **não** usam `$unwind` (ali a unidade é a solicitação; o esforço em minutos é
  somado com `$sum` direto sobre o array, evitando duplicação).
- **`$elemMatch`** garante que *o mesmo* atendimento seja da COORDENACAO **e**
  tenha mais de 30 min (sem ele, as condições poderiam ser satisfeitas por
  elementos diferentes).
- `random.seed(42)` deixa os dados reproduzíveis.

# ALUNO - CARLOS HENRIQUE CARDOSO DA SILVA ROCHA - DANIEL CARVALHO SILVA
# DATA - 11/11/2026
# BANCO DE DADOS - 4° PERIODO 