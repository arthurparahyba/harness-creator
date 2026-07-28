/// Saldo que sobra depois de reservar unidades.
pub fn saldo_disponivel(total: i64, reservado: i64) -> i64 {
    (total - reservado).max(0)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn nao_fica_negativo() {
        assert_eq!(saldo_disponivel(2, 5), 0);
    }
}
