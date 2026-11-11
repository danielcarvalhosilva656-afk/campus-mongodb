from consultas import (get_collection, consulta_find, executar,
                       PIPELINE_CATEGORIAS, PIPELINE_SETORES,
                       PIPELINE_ESTUDANTES, PIPELINE_INDICADOR)


def tabela(linhas, colunas):

    if not linhas:
        return "_Sem resultados._\n"
    out = ["| " + " | ".join(colunas) + " |",
           "|" + "---|" * len(colunas)]
    for l in linhas:
        out.append("| " + " | ".join(str(l.get(c, "")) for c in colunas) + " |")
    return "\n".join(out) + "\n"


def main():
    col = get_collection()

    fila = [{"protocolo": d["protocolo"], "estudante": d["estudante"]["nome"],
             "situacao": d["situacao"], "prioridade": d["prioridade"]}
            for d in consulta_find(col)]
    categorias = executar(col, PIPELINE_CATEGORIAS)
    setores = executar(col, PIPELINE_SETORES)
    estudantes = executar(col, PIPELINE_ESTUDANTES)
    indicador = executar(col, PIPELINE_INDICADOR)

    total = col.count_documents({"situacao": {"$in": ["ABERTA", "EM_ANALISE",
                                                      "AGUARDANDO_DOCUMENTACAO"]}})

    r = ["# Painel da Coordenação - CampusFlow\n",
         f"**Solicitações em andamento:** {total}\n",
         "## 1. Fila prioritária (Eng. de Software, prioridade >= 3, "
         "+30 min na Coordenação)\n",
         tabela(fila, ["protocolo", "estudante", "situacao", "prioridade"]),
         "## 2. Categorias que concentram mais casos\n",
         tabela(categorias, ["categoria", "quantidade", "prioridadeMedia",
                             "maiorPrioridade"]),
         "## 3. Setores com mais interações\n",
         tabela(setores, ["setor", "interacoes", "tempoMedioMin", "tempoTotalMin"]),
         "## 4. Estudantes recorrentes\n",
         tabela(estudantes, ["matricula", "nome", "solicitacoes", "emAndamento",
                             "prioridadeMedia"]),
         "## 5. Indicador final: backlog crítico por categoria\n",
         tabela(indicador, ["categoria", "backlog", "criticos",
                            "percentualCritico", "esforcoTotalMin"])]
    if indicador:
        top = indicador[0]
        r.append(f"\n**Leitura:** a categoria **{top['categoria']}** tem o maior "
                 f"percentual de casos críticos ({top['percentualCritico']}%). "
                 f"Sugestão: reforçar o atendimento nela primeiro.\n")
    if setores:
        r.append(f"**Setor mais demandado:** {setores[0]['setor']} "
                 f"({setores[0]['interacoes']} interações).\n")

    texto = "\n".join(r)
    print(texto)
    with open("relatorio.md", "w", encoding="utf-8") as f:
        f.write(texto)


if __name__ == "__main__":
    main()