<?php

declare(strict_types=1);

namespace Notas;

final class Imposto
{
    public static function baseDeCalculo(float $valor, float $desconto): float
    {
        return max(0.0, $valor - $desconto);
    }
}
