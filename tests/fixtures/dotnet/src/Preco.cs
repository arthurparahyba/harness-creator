namespace Catalogo;

public static class Preco
{
    public static decimal ComImposto(decimal valor, decimal aliquota)
        => valor * (1 + aliquota);
}
