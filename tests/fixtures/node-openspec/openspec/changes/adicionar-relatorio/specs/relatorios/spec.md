## ADDED Requirements

<!-- `MUST`/`SHALL` são exigidos pelo validador do OpenSpec em toda
     requirement, mesmo com o texto em português. -->

### Requirement: Total por intervalo de datas
O sistema MUST somar os totais dos pedidos cuja data esteja dentro do
intervalo pedido, inclusive nos extremos.

#### Scenario: Intervalo com pedidos
- **GIVEN** pedidos em 2026-01-05 e 2026-01-20
- **WHEN** o total é pedido para 2026-01-01 a 2026-01-31
- **THEN** a soma dos dois pedidos é devolvida

#### Scenario: Intervalo vazio
- **GIVEN** nenhum pedido no intervalo
- **WHEN** o total é pedido
- **THEN** zero é devolvido, não erro
