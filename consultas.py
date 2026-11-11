import os

from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "campusflow"

EM_ANDAMENTO = ["ABERTA", "EM_ANALISE", "AGUARDANDO_DOCUMENTACAO"]


def get_collection():
    return MongoClient(MONGO_URI)[DB_NAME]["solicitacoes"]


def consulta_find(col):
    filtro = {
        "estudante.curso": "Engenharia de Software",
        "situacao": {"$in": ["ABERTA", "EM_ANALISE"]},
        "prioridade": {"$gte": 3},
        "atendimentos": {
            "$elemMatch": {"setor": "COORDENACAO", "duracaoMin": {"$gt": 30}}
        },
    }
    projecao = {"_id": 0, "protocolo": 1, "estudante.nome": 1,
                "situacao": 1, "prioridade": 1}
    return list(
        col.find(filtro, projecao)
        .sort([("prioridade", -1), ("criadoEm", 1)])
        .limit(5)
    )

PIPELINE_CATEGORIAS = [
    {"$match": {"situacao": {"$in": EM_ANDAMENTO}}},
    {"$group": {
        "_id": "$categoria.nome",
        "quantidade": {"$sum": 1},
        "prioridadeMedia": {"$avg": "$prioridade"},
        "maiorPrioridade": {"$max": "$prioridade"},
    }},
    {"$project": {"_id": 0, "categoria": "$_id", "quantidade": 1,
                  "prioridadeMedia": {"$round": ["$prioridadeMedia", 2]},
                  "maiorPrioridade": 1}},
    {"$sort": {"quantidade": -1}},
]

PIPELINE_SETORES = [
    {"$match": {"situacao": {"$in": EM_ANDAMENTO}}},
    {"$unwind": "$atendimentos"},
    {"$group": {
        "_id": "$atendimentos.setor",
        "interacoes": {"$sum": 1},
        "tempoMedioMin": {"$avg": "$atendimentos.duracaoMin"},
        "tempoTotalMin": {"$sum": "$atendimentos.duracaoMin"},
    }},
    {"$project": {"_id": 0, "setor": "$_id", "interacoes": 1,
                  "tempoMedioMin": {"$round": ["$tempoMedioMin", 1]},
                  "tempoTotalMin": 1}},
    {"$sort": {"interacoes": -1}},
]

PIPELINE_ESTUDANTES = [
    {"$group": {
        "_id": {"matricula": "$estudante.matricula", "nome": "$estudante.nome"},
        "solicitacoes": {"$sum": 1},
        "emAndamento": {"$sum": {"$cond": [
            {"$in": ["$situacao", EM_ANDAMENTO]}, 1, 0]}},
        "prioridadeMedia": {"$avg": "$prioridade"},
    }},
    {"$match": {"solicitacoes": {"$gte": 2}}},
    {"$project": {"_id": 0, "matricula": "$_id.matricula", "nome": "$_id.nome",
                  "solicitacoes": 1, "emAndamento": 1,
                  "prioridadeMedia": {"$round": ["$prioridadeMedia", 2]}}},
    {"$sort": {"solicitacoes": -1, "nome": 1}},
    {"$limit": 5},
]

PIPELINE_INDICADOR = [
    {"$match": {"situacao": {"$in": EM_ANDAMENTO}}},
    {"$project": {
        "categoria": "$categoria.nome",
        "critico": {"$cond": [{"$gte": ["$prioridade", 4]}, 1, 0]},
        "esforcoMin": {"$sum": "$atendimentos.duracaoMin"},
    }},
    {"$group": {
        "_id": "$categoria",
        "backlog": {"$sum": 1},
        "criticos": {"$sum": "$critico"},
        "esforcoTotalMin": {"$sum": "$esforcoMin"},
    }},
    {"$project": {
        "_id": 0, "categoria": "$_id", "backlog": 1, "criticos": 1,
        "percentualCritico": {"$round": [
            {"$multiply": [{"$divide": ["$criticos", "$backlog"]}, 100]}, 1]},
        "esforcoTotalMin": 1,
    }},
    {"$sort": {"percentualCritico": -1, "criticos": -1}},
]

def executar(col, pipeline):
    return list(col.aggregate(pipeline))


if __name__ == "__main__":
    c = get_collection()
    print("find():", consulta_find(c))
    for nome, p in [("categorias", PIPELINE_CATEGORIAS),
                    ("setores", PIPELINE_SETORES),
                    ("estudantes", PIPELINE_ESTUDANTES),
                    ("indicador", PIPELINE_INDICADOR)]:
        print(nome, executar(c, p))