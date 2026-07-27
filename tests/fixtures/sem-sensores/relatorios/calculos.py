"""Calculos de relatorio. Nenhuma funcao aqui toca rede, disco ou planilha.

Este modulo existe na fixture para dar alvos concretos de teste: a FASE 1 da
skill deve encontrar estas funcoes e cita-las pelo nome no Plano de
Remediacao, em vez de recomendar "escreva testes".
"""


def margem_percentual(receita, custo):
    if receita == 0:
        return 0.0
    return round(((receita - custo) / receita) * 100, 2)


def normalizar_cnpj(bruto):
    digitos = "".join(c for c in str(bruto) if c.isdigit())
    return digitos.zfill(14)


def agrupar_por_vendedor(linhas):
    total = {}
    for linha in linhas:
        vendedor = linha.get("vendedor", "sem-vendedor")
        total[vendedor] = total.get(vendedor, 0) + linha.get("valor", 0)
    return total


def faixa_de_comissao(valor_total):
    if valor_total < 10000:
        return "bronze"
    if valor_total < 50000:
        return "prata"
    return "ouro"
