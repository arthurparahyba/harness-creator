package com.exemplo;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class EstoqueTest {
  @Test
  void calculaDisponivel() {
    assertEquals(7, new Estoque().disponivel(10, 3));
  }
}
