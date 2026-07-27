package com.exemplo;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class FaturaTest {
  @Test
  void aplicaDesconto() {
    assertEquals(90.0, new Fatura().comDesconto(100.0, 10.0), 0.001);
  }
}
