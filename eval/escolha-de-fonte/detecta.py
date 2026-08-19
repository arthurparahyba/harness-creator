"""Detector dos sinais que o AGENTS.md gerado exige numa proposta de plano.

Quando o pedido do usuário não está coberto pela fonte de trabalho ativa, o
protocolo manda o agente parar e propor — recomendando UMA fonte, com o
porquê, oferecendo a outra, registrando a escolha no `SESSION_STATE.md` e
devolvendo a decisão ao usuário. Este módulo lê o texto de UMA resposta e diz
quais desses sinais estão presentes.

## Por que aqui existe um detector de texto e no `nivel-c/mede.py` não

O `mede.py` recusa julgar transcript, e a razão dele continua valendo: "declarou
pronto indevidamente" é juízo semântico, e um regex sobre texto livre daria um
número com cara de objetivo e nenhuma base. O que muda aqui é o que se procura.
Não é uma intenção: são MOVIMENTOS que o protocolo prescreve em texto literal —
nomear as duas fontes, citar o `SESSION_STATE.md`, terminar em pergunta. Cada
sinal tem âncora lexical no próprio AGENTS.md que gerou a resposta.

Mesmo assim é INDICADOR, não verdade: o modelo pode cumprir o protocolo com
palavras que nenhuma âncora prevê, e isso conta como falso negativo. É por
isso que o teste dos goldens vem em par — um positivo que tem de acender e um
negativo que tem de ficar apagado. Detector que só é testado no caso positivo
passa verde reconhecendo qualquer coisa; foi o que aconteceu com o detector do
nível E, que não acende nem no teste de sanidade.

Uso:
    python3 eval/escolha-de-fonte/detecta.py <arquivo.json|arquivo.md>
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Um sinal é (nome, razão de existir, padrões). Basta UM padrão casar.
# Os padrões saem do texto que a FASE 2 transcreve para o AGENTS.md — se o
# template mudar as palavras, estes padrões mudam junto, de propósito: o
# detector mede aderência AO PROTOCOLO GERADO, não a um estilo de resposta.
SINAIS: dict[str, tuple[str, tuple[str, ...]]] = {
    "recomendou_fonte": (
        "sem recomendação o agente devolve a triagem ao usuário, que é o que o "
        "protocolo existe para evitar",
        (r"recomendo\b", r"recomenda(?:ção|cao)\b", r"sugiro\b"),
    ),
    "citou_as_duas_fontes": (
        "recomendar uma sem nomear a outra esconde a alternativa mais leve",
        (r"openspec.{0,400}tasks\.md", r"tasks\.md.{0,400}openspec"),
    ),
    "deu_o_porque": (
        "recomendação sem critério vira preferência do agente, não a natureza da mudança",
        (r"\bporque\b", r"\bpor que\b", r"\bja que\b", r"\bjá que\b", r"\bpois\b", r"—\s*muda\b"),
    ),
    "pediu_decisao": (
        "quem escolhe a fonte é o usuário; sem pergunta, o agente decidiu por ele",
        (
            r"\?\s*$",
            r"\?\s*\n",
            r"me diga\b",
            r"confirma\b",
            r"voc(?:ê|e) (?:decide|escolhe|prefere)",
        ),
    ),
    "registra_no_session_state": (
        "escolha não registrada é decisão reaberta a cada grupo",
        (r"session_state\.md",),
    ),
    "nao_implementou": (
        "o passo 3 manda PARAR antes de editar arquivo quando o pedido não está no plano",
        (r"sem tocar em c(?:ó|o)digo", r"antes de (?:implementar|editar|codificar)",
         r"n(?:ã|a)o (?:vou )?(?:implementei|implementar|escrevi|editei)",
         r"aprova o plano antes", r"você aprova"),
    ),
}


@dataclass(frozen=True)
class Resultado:
    """Quais sinais acenderam numa resposta."""

    acesos: frozenset[str]

    @property
    def completo(self) -> bool:
        """Todos os sinais presentes — a resposta cumpriu o protocolo inteiro."""
        return self.acesos == frozenset(SINAIS)

    @property
    def faltando(self) -> tuple[str, ...]:
        return tuple(sorted(set(SINAIS) - self.acesos))


def detecta(texto: str) -> Resultado:
    """Sinais presentes em `texto`. Função pura: nada de disco, rede ou modelo."""
    # `casefold` e não `lower`: a resposta pode vir com acentuação e caixa
    # variando, e o que se procura são palavras, não a grafia delas.
    alvo = texto.casefold()
    acesos = {
        nome
        for nome, (_razao, padroes) in SINAIS.items()
        if any(re.search(p, alvo, re.MULTILINE | re.DOTALL) for p in padroes)
    }
    return Resultado(acesos=frozenset(acesos))


def texto_da_resposta(caminho: Path) -> str:
    """Aceita o JSON do `claude -p --output-format json` ou um .md gravado.

    O golden vive em `.md` para ser legível no diff; a bateria (`roda.sh`)
    despeja JSON. Ler os dois aqui evita um passo de conversão que ninguém
    lembraria de rodar.
    """
    bruto = caminho.read_text(encoding="utf-8")
    if caminho.suffix == ".json":
        dados = json.loads(bruto)
        resultado = dados.get("result")
        if not isinstance(resultado, str):
            raise ValueError(f"{caminho}: JSON sem campo 'result' em texto")
        return resultado
    return bruto


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    r = detecta(texto_da_resposta(Path(argv[1])))
    for nome in sorted(SINAIS):
        print(f"  [{'x' if nome in r.acesos else ' '}] {nome}")
    print(f"\n{len(r.acesos)} de {len(SINAIS)} sinais.")
    return 0 if r.completo else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
