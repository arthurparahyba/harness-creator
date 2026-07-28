export function total(itens: number[]): number {
  return itens.reduce((a, b) => a + b, 0);
}
