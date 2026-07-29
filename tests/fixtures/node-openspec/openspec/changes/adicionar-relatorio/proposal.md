# Relatório de totais por período

<!-- Os cabeçalhos estruturais são em INGLÊS por exigência do validador do
     OpenSpec: `## Why` e `## What Changes` são procurados pelo nome. O
     conteúdo pode ser em português; a estrutura, não. -->

## Why
Hoje só existe o total por pedido. O fechamento mensal é feito à mão somando
pedidos um a um, e o erro só aparece na conferência.

## What Changes
Endpoint que agrega pedidos por intervalo de datas.

Fora do escopo: exportação em CSV e gráficos — o pedido é o número, não a
apresentação.
