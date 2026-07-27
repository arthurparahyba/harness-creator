import { expect, test } from "vitest";
import { Contador } from "./Contador";

test("componente existe", () => {
  expect(typeof Contador).toBe("function");
});
