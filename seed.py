import os
import random
from datetime import datetime, timedelta

from pymongo import MongoClient, ASCENDING, DESCENDING

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "campusflow"

random.seed(42)  

CURSOS = ["Engenharia de Software", "Ciência da Computação", "Direito",
          "Administração", "Psicologia"]
CATEGORIAS = ["Aproveitamento de Disciplina", "Trancamento de Matrícula",
              "Segunda Chamada", "Declaração", "Revisão de Nota"]
SITUACOES = ["ABERTA", "EM_ANALISE", "AGUARDANDO_DOCUMENTACAO",
             "CONCLUIDA", "CANCELADA"]
SETORES = ["SECRETARIA", "COORDENACAO", "FINANCEIRO", "BIBLIOTECA", "NTI"]
TAGS = ["DOCUMENTACAO", "URGENTE", "PRAZO", "RECURSO", "DUVIDA"]
NOMES = ["Ana Souza", "Bruno Lima", "Carla Dias", "Diego Rocha", "Elisa Prado",
         "Fábio Nunes", "Gabriela Melo", "Henrique Alves", "Isabela Costa",
         "João Pereira", "Karina Teles", "Lucas Barros", "Marina Freitas",
         "Nicolas Ramos", "Olívia Cardoso", "Pedro Matos", "Quésia Lopes",
         "Rafael Duarte", "Sabrina Viana", "Tiago Moura"]


def gerar_estudantes():
    return [{"nome": n, "matricula": f"2024{i:04d}", "curso": random.choice(CURSOS)}
            for i, n in enumerate(NOMES, start=1)]


def gerar_solicitacoes(qtd=200):
    estudantes = gerar_estudantes()
    base = datetime(2026, 9, 1)
    docs = []
    for i in range(1, qtd + 1):
        criado = base + timedelta(days=random.randint(0, 60),
                                  hours=random.randint(0, 23))
        atendimentos = [{
            "setor": random.choice(SETORES),
            "duracaoMin": random.choice([5, 8, 10, 15, 20, 30, 35, 45, 60]),
            "data": criado + timedelta(days=random.randint(0, 5)),
        } for _ in range(random.randint(1, 4))]
        docs.append({
            "protocolo": f"SOL-{1000 + i}",
            "estudante": random.choice(estudantes),
            "categoria": {"nome": random.choice(CATEGORIAS)},
        
            "situacao": random.choices(SITUACOES, weights=[30, 25, 15, 25, 5])[0],
            "prioridade": random.randint(1, 5),
            "tags": random.sample(TAGS, random.randint(1, 3)),
            "criadoEm": criado,
            "atendimentos": atendimentos,
        })
    return docs


def main():
    col = MongoClient(MONGO_URI)[DB_NAME]["solicitacoes"]
    col.drop()  
    col.insert_many(gerar_solicitacoes())
    col.create_index([("situacao", ASCENDING), ("prioridade", DESCENDING)])
    print(f"{col.count_documents({})} solicitações inseridas em {DB_NAME}.solicitacoes")


if __name__ == "__main__":
    main()