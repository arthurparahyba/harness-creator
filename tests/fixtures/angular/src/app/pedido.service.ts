export class PedidoService {
  total(precos: number[]): number {
    return precos.reduce((a, b) => a + b, 0);
  }
}
