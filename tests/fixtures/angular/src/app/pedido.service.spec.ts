import { PedidoService } from './pedido.service';

describe('PedidoService', () => {
  it('soma os precos', () => {
    expect(new PedidoService().total([1, 2])).toBe(3);
  });
});
