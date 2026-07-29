export interface Item {
  preco: number;
  quantidade: number;
}

export const totalDoPedido = (itens: Item[]): number =>
  itens.reduce((soma, i) => soma + i.preco * i.quantidade, 0);
