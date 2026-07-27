import { expect, test } from "vitest";
import { totalDoPedido } from "../src/total";

test("soma preco por quantidade", () => {
  expect(totalDoPedido([{ preco: 10, quantidade: 2 }])).toBe(20);
});
