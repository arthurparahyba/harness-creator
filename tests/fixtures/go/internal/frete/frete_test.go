package frete

import "testing"

func TestCalcular(t *testing.T) {
	if got := Calcular(10, 2); got != 800 {
		t.Fatalf("esperado 800, veio %d", got)
	}
}
