import { expect, test } from "vitest";
import { emReais } from "./formata";

test("formata centavos", () => {
  expect(emReais(1050)).toBe("R$ 10.50");
});
