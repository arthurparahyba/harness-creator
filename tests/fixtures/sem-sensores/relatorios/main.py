"""Entrypoint. Importa dependencia de sistema no NIVEL DO MODULO de proposito.

E o caso que a skill precisa detectar: um `import openpyxl` aqui em cima faz
qualquer teste que importe este modulo morrer com ImportError se a
dependencia nao estiver instalada. A recomendacao de sensores tem de vir
acompanhada de um conftest com stub — senao o usuario aceita a proposta e
recebe um erro no lugar do primeiro teste verde.
"""

import sys

import openpyxl
import requests

from relatorios.calculos import agrupar_por_vendedor, faixa_de_comissao, margem_percentual

ENDPOINT = "https://api.interno.exemplo/vendas"


def carregar_planilha(caminho):
    wb = openpyxl.load_workbook(caminho)
    aba = wb.active
    linhas = []
    for vendedor, valor, custo in aba.iter_rows(min_row=2, values_only=True):
        linhas.append({"vendedor": vendedor, "valor": valor, "custo": custo})
    return linhas


def publicar(payload):
    return requests.post(ENDPOINT, json=payload, timeout=30).status_code


def main():
    linhas = carregar_planilha(sys.argv[1])
    por_vendedor = agrupar_por_vendedor(linhas)
    payload = {
        vendedor: {
            "total": total,
            "faixa": faixa_de_comissao(total),
            "margem": margem_percentual(total, sum(l["custo"] for l in linhas)),
        }
        for vendedor, total in por_vendedor.items()
    }
    print(publicar(payload))


if __name__ == "__main__":
    main()
