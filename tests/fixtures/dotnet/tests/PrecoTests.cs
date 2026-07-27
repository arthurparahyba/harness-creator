using Xunit;

namespace Catalogo.Tests;

public class PrecoTests
{
    [Fact]
    public void AplicaImposto()
    {
        Assert.Equal(110m, Preco.ComImposto(100m, 0.10m));
    }
}
