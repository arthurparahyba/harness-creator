<?php

declare(strict_types=1);

use Notas\Imposto;
use PHPUnit\Framework\TestCase;

final class ImpostoTest extends TestCase
{
    public function testNuncaFicaNegativa(): void
    {
        $this->assertSame(0.0, Imposto::baseDeCalculo(10.0, 25.0));
    }
}
