export const emReais = (centavos: number): string =>
  `R$ ${(centavos / 100).toFixed(2)}`;
