# frozen_string_literal: true

# Regras de comissionamento de vendedores.
module Comissao
  FAIXAS = { 0 => 0.02, 10_000 => 0.05, 50_000 => 0.08 }.freeze

  def self.percentual(total)
    FAIXAS.select { |piso, _| total >= piso }.values.max
  end
end
