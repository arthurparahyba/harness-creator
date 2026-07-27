package frete

// Calcular devolve o frete em centavos para a distancia informada.
func Calcular(distanciaKm int, pesoKg float64) int {
	base := 500
	return base + distanciaKm*10 + int(pesoKg*100)
}
