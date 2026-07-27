package com.exemplo;

public class Fatura {
  public double comDesconto(double valor, double percentual) {
    return valor * (1 - percentual / 100);
  }
}
