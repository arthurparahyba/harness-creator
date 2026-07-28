# frozen_string_literal: true

require "comissao"

RSpec.describe Comissao do
  it "usa a faixa mais alta atingida" do
    expect(described_class.percentual(60_000)).to eq(0.08)
  end
end
