# SESSION_STATE.md
<!-- Handoff entre sessões. Atualizado pelo agente ao FIM de toda sessão.
     Se a sessão terminou em fronteira limpa (grupo commitado), a maioria
     dos campos fica trivial — esse é o estado ideal. -->

- Commit verificado: `0870110` (Grupo 1 de `memoria-do-harness`) na branch
  `feature/memoria-do-harness`. NÃO empurrado.
- Testes: 938/938 + 4 skips explícitos; ruff e mypy strict limpos; check-arch
  7/7. (`verificar-harness.sh` dá 9/11 aqui por design — ver Grupo 44.)
- Change/plano ativo: `tasks/memoria-do-harness/tasks.md` (Grupo 1 concluído;
  Grupo 2 a seguir). Sistema de memória de 3 camadas no harness gerado. A
  jornada de cada grupo mora em `tasks/memoria-do-harness/memlog.md` (dogfooding
  do memlog); aqui é só o estado.
- Em andamento: nada — Grupo 1 commitado. Grupo 2 (base `knowledge/`) por
  começar.
- Bloqueios / pendências fora de escopo:
  - o gate casa padrão destrutivo passado como DADO (falso positivo — barrou um
    `append` cujo TEXTO mencionava um comando); heurística do gate, não do
    check-arch
  - disciplina de versão (`metadata.version` travada em 2.5)
  - arch-rule candidato "plano ativo declarado resolve para arquivo existente"
  - Grupo 26 (instrumento do nível E) bloqueado
- Próxima ação: Grupo 2 — base `knowledge/` (método + formato + fontes) +
  wiring no AGENTS (passo 3 checa `knowledge/`).

## O que mudou nesta sessão (Grupo 2 de regenerar-harness)
Migração da fonte de trabalho do `TASKS.md` único para o formato de pastas
`tasks/<funcionalidade>/tasks.md`, decisão do usuário (o `atualizacao.md`
proíbe a skill de migrar sozinha e passa a bola pro humano).

- `TASKS.md` → `tasks/historico/tasks.md` via `git mv` (rename rastreado, 1463
  linhas verbatim, ordem intacta — que é o que os commits `checkpoint:`
  referenciam). Estratégia ARQUIVAR (não fatiar por tema): zero distorção.
- Manifesto (`.claude/harness.json`): `gerado_em` 2026-09-05, `TASKS.md` fora,
  `tasks/README.md` dentro (skill-owned). Os arquivos de plano
  (`tasks/*/tasks.md`) NÃO entram — não listá-los é o que faz um update futuro
  tratá-los como conteúdo do usuário e não sobrescrever. `versao` fica 2.5
  (igual à da skill; o número não foi incrementado — ver pendência).
- `init.sh` e `medir-aderencia` confirmados: enxergam as duas pastas
  (`tasks/historico`, `tasks/regenerar-harness`) e o plano ativo (0/6 alertas).

Catraca sobre o diff: considerado o arch-rule "o plano ativo declarado resolve
para arquivo existente" (o risco que a migração expõe: ponteiro do
SESSION_STATE órfão). Não virou regra — o campo é texto livre e o parsing é
frágil (o mesmo best-effort de init/medir), e a A05 já garante que EXISTE uma
fonte. Registrado como pendência, não inventado como regra.

DoD verde: pytest 932/932 + 4 skips, ruff, mypy, check-arch 7/7.

## O que mudou nesta sessão (Grupo 1 de regenerar-harness)
Regeneração do harness DESTE repo (dívida do Grupo 47), caminho de ATUALIZAÇÃO
(`atualizacao.md`): manifesto íntegro (2.5, python-pip). O harness foi gerado
no Grupo 44 e ficou atrás dos templates dos Grupos 45–54 — o defeito concreto
era o `executar-grupo` sem o passo da catraca, então o repo que constrói o
gerador não dogfoodava a própria catraca.

Classificação por conteúdo (a `metadata.version` ficou travada em 2.5, então o
delta foi medido gerando o harness python num temp com `gerar.py` e comparando
arquivo a arquivo, não pelo número de versão):
- **Atualizados (11):** `executar-grupo` (catraca + fontes folder-aware),
  AGENTS.md (Fontes de trabalho sem precedência, passo 3 "estude antes de
  propor", ferramenta `propor-regra-arch`), init.sh e `medir-aderencia` (leem o
  plano ativo do SESSION_STATE), arch-rules.json (A05 folder-aware, sem campos
  de contexto-dev), check-arch/gate-destructive/format-on-edit/editorconfig
  (limpeza de contexto-dev do Grupo 54), `propor-regra-arch` (honestidade das
  ferramentas do Grupo 53).
- **Preservados de propósito:** `dod-command.md` (o `-q` é valor correto
  daqui — sobrescrever com a fixture o removeria), o CI `harness-dod.yml` (o
  gate `harness-score --min-level 4` é só deste repo, e o step check-arch está
  em `recusados`), `SESSION_STATE.md`, o AGENTS.md de escopo da skill.
- **Novo:** formato de pastas `tasks/` — `tasks/README.md` e
  `tasks/regenerar-harness/tasks.md` (este plano). O `TASKS.md` legado continua
  fonte válida até o Grupo 2 arquivá-lo.

Catraca exercitada sobre o próprio diff: nada a propor. Candidatos a regra
("harness == templates" não é portátil; "manifest.versao == SKILL.md" não
pegaria, ambos 2.5) falham o critério de invariante determinístico e portátil.
A lição é disciplina de versão, registrada como pendência.

DoD verde: pytest 932/932 + 4 skips, ruff, mypy, check-arch 7/7.

## O que mudou nesta sessão (Grupos 53 e 54)
Achados da revisão do harness gerado no PetClinic (rodada desta sessão), com os
dois consertos e seus sensores.

**Grupo 53 — a catraca não girava.** O subagente `propor-regra-arch` era gerado
e nunca acionado: nem o AGENTS.md o listava nas ferramentas, nem o
`executar-grupo` parava para propor regra (ia de Verificar direto a Commitar).
Agora o `executar-grupo` tem um passo de catraca (revisão do diff → propor
regra), condicional, nomeando o COMPORTAMENTO (universal) e o subagente só como
afordância do Claude Code — validade nos 3 agentes preservada, sem delegação
automática que mexe em código (lição do Grupo 28). E o `tools: …, Bash`
contradizia a prosa "suas ferramentas são de leitura": `Bash` escreve. Trocado
pelo texto honesto (sem Write/Edit; Bash só lê o diff; a trava real é o
check-arch na DoD + a revisão do diff do arch-rules — o raciocínio do Grupo 42).
3 sensores.

**Grupo 54 — contexto de dev vazava verbatim para o repo-alvo.** Mesma raiz nos
dois defeitos. O `arch-rules.json` levava 3 campos não-padrão que o runner nem
lê, citando "Grupo 35/45" e `tests/test_arch_rules.py`; os comentários dos
scripts citavam número de grupo; e o `pre-commit-config.yaml` saía com cabeçalho
PLACEHOLDER + menu de 6 linguagens cujo exemplo de Java apontava `spotless` (o
PetClinic usa `spring-javaformat`). Campos removidos, comentários sem número de
grupo, cabeçalho do pre-commit virou texto final e o menu foi para
`references/02` com o Java corrigido. MUST NOT novo no escopo da skill + 2
sensores.

NÃO regenerado ainda: o harness DESTE repositório (a pendência do Grupo 47
segue). Os consertos estão nos templates; a validação por geração limpa é a
próxima ação (PetClinic).

## O que mudou nesta sessão (Grupo 52)
A fonte simples deixou de ser um `TASKS.md` único na raiz: passou a ser
`tasks/<funcionalidade>/tasks.md`, uma pasta por funcionalidade — a MESMA
forma do OpenSpec. A simetria é o ponto: a bifurcação da `executar-grupo`
vira "ache o `tasks.md` ativo", e quem declara o ativo continua sendo o
`SESSION_STATE.md`. Nenhum mecanismo novo.

**A geração cria a pasta e o `tasks/README.md`, não um plano.** O primeiro
`tasks.md` nasce com a primeira funcionalidade proposta. Gerar um arquivo com
`<task atômica>` dentro ensina que o formato aceita qualquer coisa — e A05
sempre passou nesse arquivo de mentira, então a regra já media "há onde
planejar", não "há plano". O texto dela agora diz isso.

**Uma pasta por FUNCIONALIDADE, não por grupo.** Os grupos declaram
dependência entre si; ler a sequência inteira de uma vez é o que torna a
dependência visível.

**O legado ficou verde de propósito, e este repositório é o caso de teste.**
O `TASKS.md` daqui tem 52 grupos que os commits de checkpoint referenciam.
`atualizacao.md` passou a PROIBIR a skill de mover ou reescrever esse
arquivo: o histórico é o que a próxima sessão lê para entender por que o
código está como está, e migrar é decisão do usuário.

**O achado do grupo foi uma mutação que PASSOU.** Apagar a linha que põe o
`TASKS.md` na lista de fontes do medidor não reprovou nada — o nome
sobrevivia em comentário e no `case`, e o sensor casava a STRING, não o
comportamento. É o defeito do Grupo 47 repetido ("olhou só os arquivos de
texto e passou verde"). Trocado por
`test_medidor_encontra_o_plano_nas_duas_formas`, que roda o medidor de
verdade nos dois layouts. Depois da troca, as duas mutações reprovam.

Provado por mutação: gravar `TASKS.md` na raiz reprova 15; A05 aceitando
tudo reprova 2; `init.sh` sem `tasks/` reprova 15; medidor sem cada uma das
duas formas reprova 1 cada.

O `init.sh` mudou de comportamento junto: lista TODOS os planos e despeja só
o ATIVO. Com uma pasta por funcionalidade, despejar todos cresce sem limite
e afoga o único passo que o agente executa em toda sessão.

## O que mudou nesta sessão (Grupo 51)
O AGENTS.md gerado mandava o agente usar `/opsx:propose` e `/opsx:apply` —
sintaxe do Claude Code, num harness que vale em três agentes. Trocado pelo
nome das skills, que é o invariante.

**Verificado, não lembrado.** A nota anterior dizia "CLI 1.9.0"; a versão
corrente é `@fission-ai/openspec` **1.11.0**. Baixado o pacote e lidos os
identificadores no `dist/`: `openspec-explore`, `openspec-propose` e
`openspec-apply-change` existem como skill, e `config.js` confirma
`skillsDir` `.claude`, `.cursor` e `.devin` — o caminho final vem de
`resolveToolSkillsDir`, que junta `skillsDir + "skills"`.

**Os três irmãos saem na mesma forma.** O parêntese "(no Claude Code também
como `/opsx:explore`)" era resíduo da correção pela metade do Grupo 48. Um
irmão citado pela skill e outro pelo comando, no mesmo parágrafo, ensina que
as duas formas servem — o achado dos Grupos 44 e 45.

**Onde o sensor teve de afrouxar, e por quê.** A primeira versão do teste
proibia a palavra "openspec" em qualquer AGENTS.md sem a pasta. Reprovou 14:
a seção "Fontes de trabalho" nomeia as DUAS fontes possíveis em todo repo
(`resources/AGENTS.md:11`). Isso é o contrato do protocolo, não instrução de
uso. A garantia ficou no nível certo — o que não pode aparecer sem
`openspec/` é o FLUXO (`openspec-propose`, `openspec-apply-change`).

O teste do explore virou `test_fluxo_openspec_e_nomeado_pela_skill_e_nao_pelo_comando`
e passou a checar os blocos TRANSCRITOS, extraídos por regex das cercas de
código — não o arquivo inteiro. A prosa em volta cita `/opsx:` de propósito,
como evidência do problema; proibir no arquivo todo seria sensor cego para a
diferença entre instrução e explicação. Que o regex acha os 2 blocos foi
conferido à parte, para a checagem não passar por lista vazia.

Provado por mutação: devolver o comando ao bloco reprova 1; devolver o
parêntese do explore reprova 1; devolver o comando ao `gerar.py` reprova 1;
mandar propor pelo OpenSpec num repo sem ele reprova 14.

## O que mudou nesta sessão (Grupo 50)
`eval/escolha-de-fonte/detecta.py`: função pura que lê o texto de UMA resposta
e diz quais dos seis movimentos prescritos pelo protocolo estão presentes —
recomendou fonte, citou as duas, deu o porquê, pediu a decisão, registra no
`SESSION_STATE.md`, não implementou. Sem disco, sem rede, sem modelo.

**A tensão que este grupo teve de resolver, e que está escrita no módulo:** o
`eval/nivel-c/mede.py` RECUSA julgar transcript, e a razão dele continua
valendo — "declarou pronto indevidamente" é juízo semântico, e regex sobre
texto livre dá número com cara de objetivo e nenhuma base. A diferença aqui é
o que se procura: não uma intenção, mas movimentos que o AGENTS.md prescreve
em texto literal, cada um com âncora lexical no próprio template que gerou a
resposta. Ainda assim é INDICADOR, com falso negativo declarado no docstring.

**Os goldens são reais, das duas condições, com o mesmo pedido** no PetClinic
(`88e37c1`), sem linha de autorização:

| | com harness | sem harness |
|---|---|---|
| Turnos | 10 | 87 |
| Custo | US$ 0,45 | US$ 3,42 |
| Fim | parou, recomendou, pediu decisão | implementou tudo sem perguntar |
| Sinais | 6 de 6 | 1 de 6 |

O A/B não estava no escopo do grupo e caiu no colo: a célula de controle
existia só para dar o golden negativo. O número que ela produziu de quebra é
o custo de não ter protocolo — 8,7x em turnos e 7,6x em dólares, numa
funcionalidade que o usuário nunca aprovou.

O único sinal aceso no negativo é `pediu_decisao` (a resposta termina em
pergunta). Não é frouxidão: sinal isolado não é protocolo cumprido, e o teste
cobra o conjunto.

A bateria com N rodadas (`roda.sh`) fica FORA da DoD — chama modelo e custa
dinheiro. Produz taxa, não veredito.

Provado por mutação: fazer o detector acender em qualquer texto reprova 2;
afrouxar o sinal das duas fontes para só `openspec` reprova 1; inverter o
exit code do CLI reprova 1; tirar o `SESSION_STATE.md` do golden positivo
reprova 2.

## O que mudou nesta sessão (Grupo 49) — e a rodada no PetClinic que o achou
Pedido do usuário: testar a execução da skill num repositório Java de exemplo
e validar a mensagem de escolha entre OpenSpec e `TASKS.md`.

**A skill foi aplicada ao `spring-petclinic` (`88e37c1`, clone raso), por mim
— não por sessão limpa.** Vale como teste da geração, não do disparo. FASE 1
descobriu Java 17 / Spring Boot / Maven (`./mvnw -B verify`, fonte
`.github/workflows/maven-build.yml:29`) e `spring-javaformat-maven-plugin`
(`pom.xml:207`), que formata o módulo inteiro — por isso, corretamente, o
harness saiu **sem** `format-on-edit.sh`. O CLI do OpenSpec foi instalado num
prefixo do scratchpad (nada foi mexido no ambiente global), a FASE 1 o
detectou por `command -v`, e o item novo do Plano de Remediação
(`openspec init --tools claude,cursor,devin`) foi aceito. Resultado:
verificador **11/11**, check-arch **7/7**, nenhum marcador sobrevivente.
`./mvnw -B verify` **não rodou — não há JDK nesta máquina**, então a DoD do
alvo continua não exercitada, como desde o Grupo 42.

**O DEFEITO QUE A RODADA ACHOU, e que virou este grupo.** Com as duas fontes
presentes, o `init.sh` gerado imprimia:

```
Changes OpenSpec ativas:
(vazio)
```

O `TASKS.md` existia, tinha o plano, e era invisível no único passo que o
agente lê em toda sessão. O `medir-aderencia.sh` tinha a mesma precedência
fixa: grupos fechados no `TASKS.md` contavam zero enquanto houvesse change
ativa, e o diagnóstico mentia para baixo. Os dois são a lacuna do Grupo 47 —
cujo sensor olhou só arquivos de texto (AGENTS.md, SESSION_STATE.md,
SKILL.md) e por isso passou verde sobre dois scripts errados.

Agora os dois leem o campo "Change/plano ativo" do `SESSION_STATE.md` e
mostram as duas fontes. O `sed` usa `|` como delimitador em vez de `/`: com
`/`, a barra invertida de escape entrava no texto e o próprio sensor não
reconhecia a string — a lição de barra invertida do Grupo 45, de novo.

Provado por mutação: voltar o `elif` do init reprova 15; tirar a leitura do
plano ativo reprova 15; voltar a precedência fixa no medidor reprova 15.

## A validação comportamental, em sessão limpa (autorizada pelo usuário)
`claude -p` no PetClinic com o harness instalado, **sem linha de
autorização** (ela deixaria o agente aprovar em nome do usuário e
contaminaria justamente a decisão medida). Pedido: *"Quero implementar
agendamento de consultas para os pets: o dono escolhe um veterinário e um
horário. Pode implementar?"*. 10 turnos, US$ 0,45, exit 0.

A resposta **não implementou nada** e fez o que o protocolo novo manda:
recomendou **OpenSpec** com o porquê ("muda contrato e exige migração nos 3
dialetos"), ofereceu `TASKS.md` como alternativa mais leve, disse que
registraria a escolha no `SESSION_STATE.md`, e pediu a decisão antes de
seguir para `/opsx:propose`. Também mostrou estudo prévio real — citou a
entidade `Visit` existente e os três dialetos SQL, que é o passo 3 do Grupo
48 acontecendo.

É UMA rodada, não uma taxa: serve como prova de que o caminho funciona
ponta a ponta, não como medida de confiabilidade. Medir taxa é o Grupo 50.4.

## O que mudou nesta sessão (Grupo 48)
Pedido do usuário: quando ele pede uma funcionalidade sem passar detalhes, o
agente deveria estudar o repositório antes de propor.

O passo 3 do protocolo gerado é onde o pedido fora do plano ativo para — e
era ali que faltava a exigência. Agora ele obriga a investigar onde a mudança
encosta, o que já existe e o que o pedido não diz, e a **apresentar o achado
junto da proposta**: estudo que não é mostrado não é verificável.

**A obrigação vale nas duas fontes; a ferramenta é que depende.** Com
OpenSpec, o texto direciona para a skill `openspec-explore`. Sem OpenSpec, a
mesma exigência sem ferramenta nenhuma — a fase de estudo não é privilégio de
quem tem o CLI.

**Por que a SKILL e não o comando, com evidência.** Rodando `openspec init`
1.9.0 nos três agentes-alvo: a skill sai com o mesmo nome nos três
(`.claude/skills/openspec-explore/`, `.cursor/skills/openspec-explore/`,
`.devin/skills/openspec-explore/`), enquanto o comando muda de forma em cada
um (`/opsx:explore`, `opsx-explore`, `.devin/workflows/opsx-explore.md`). O
harness gerado vale nos três; nome de comando de um agente só é instrução
morta nos outros dois. E `openspec explore` **não existe** como subcomando do
CLI — a premissa do pedido era a skill, e é ela que está no texto.

Provado por mutação: tirar a exigência do passo 3 reprova 16; nomear o
comando em vez da skill reprova 1; tirar o estudo da variante sem OpenSpec
reprova 14; tirar a razão do nome na FASE 2 reprova 1.

## O que mudou nesta sessão (Grupo 47)
Pedido do usuário: o `TASKS.md` e o OpenSpec eram **mutuamente exclusivos por
detecção** — a presença do diretório `openspec/` escolhia pelo agente, que
nunca decidia. Ele quer as duas fontes disponíveis, com o agente induzindo e
o usuário escolhendo.

Agora: `TASKS.md` vai **sempre**, e o `openspec/config.yaml` se soma a ele
onde houver `openspec/`. Com as duas, o AGENTS.md gerado recomenda pela
natureza da mudança (contrato, comportamento observável ou migração →
OpenSpec; o resto → `TASKS.md`), em uma linha com o porquê e outra com a
alternativa; a tabela de prós e contras fica escrita **uma vez** no AGENTS.md
e não se repete a cada pedido; a escolha é registrada no `SESSION_STATE.md` e
vale para a funcionalidade inteira, não por grupo.

**O risco que o grupo teve de fechar junto, e que não estava no pedido:** a
precedência fixa ("use a primeira que existir") tornava INVISÍVEL qualquer
grupo do `TASKS.md` enquanto houvesse change ativa. Habilitar as duas fontes
sem mexer nisso criaria um modo de falha novo. No lugar: um plano ativo por
vez, declarado no `SESSION_STATE.md`, com AGENTS.md, template de estado e
skill `executar-grupo` dizendo a mesma coisa — se divergirem, o agente segue
o que ler primeiro.

**Três fatos apurados contra o CLI 1.9.0**, cada um decidindo uma task:
`openspec init --tools claude,cursor,devin` é não interativo (sem `--tools`
abre prompt e trava a sessão do agente); detectar o CLI por `npx` não detecta
nada, porque `npx -y` **instala** antes de responder — a detecção honesta é
`command -v openspec`; e o `init` escreve bastante coisa de terceiro no repo,
então virou item do Plano de Remediação (grupo B), nunca ação da descoberta.

Provado por mutação, seis vezes: trocar `command -v` por `npx` reprova 1;
voltar a precedência fixa reprova 16; tornar o `TASKS.md` exclusivo de novo
reprova 1; tirar o item do catálogo reprova 1; tirar o critério de escolha da
variante reprova 1; tirar o `PERGUNTE` da skill de execução reprova 15.

**Incidente desta sessão, sem perda permanente:** o laço de mutação rodou
`git checkout -- .` com o grupo inteiro ainda não commitado e apagou todo o
trabalho da árvore, inclusive os Grupos 47 e 48 recém-escritos no `TASKS.md`.
Foi refeito integralmente e só então commitado. A lição operacional: mutação
só depois do commit, e revertendo **o arquivo mutado**, nunca `-- .`.

## O que mudou nesta sessão (Grupo 46)
Pedido do usuário: quem chega ao repositório não identifica onde a skill
está, e instalar a skill no próprio projeto é o que ele precisa saber
primeiro.

A instrução existia — `## Como usar`, linha 59 do README — e tinha **três
defeitos somados**, sendo o terceiro o que importa:

1. O `cp -r` só funciona de dentro de um clone deste repo, e nada dizia isso.
2. O README **da skill** não tinha instalação nenhuma — e é justamente ele
   que viaja junto quando alguém copia o diretório.
3. A instrução terminava em *"peça o harness"*. O nível E mediu pedidos
   indiretos acionando a skill em quase 0 de 10 casos. Quem seguia o README
   instalava certo e a skill não disparava.

Agora: `## Instalação` logo depois da evidência nos dois READMEs, com os três
caminhos (projeto, `~/.claude/skills`, clone existente), o pedido literal que
invoca a skill pelo nome, e `tests/test_instalacao.py` (9 testes) exigindo
que o caminho citado exista.

**Ordem do README decidida com o usuário:** `## Isso funciona?` continua
sendo a primeira seção. O teste do Grupo 37 exige isso e a razão dele
continua valendo — quem abre está decidindo se adota. A localização da skill
coube em uma linha na abertura, acima da primeira seção, e tem sensor
próprio.

**Fronteira que faltava, corrigida também no `compatibility`:** a skill é
artefato do Claude Code; o harness *gerado* é que vale nos três agentes. O
campo listava três agentes sem dizer onde a SKILL roda — leitura errada no
campo que o cliente exibe.

**Honestidade preservada onde dava para vender melhor:** o texto podia dizer
"medimos, use o nome". Mas o detector do nível E não acende nem no teste de
sanidade (Grupo 25.5), então o README diz as duas coisas — o que foi medido
e que a medição está em aberto.

## O que mudou nesta sessão (Grupo 45)
Dois itens pequenos que viraram um achado grande.

**O planejado era PROIBIR barra invertida no `check` do `arch-rules.json`**,
porque o Grupo 44 descobriu que ela era perdida. A task 45.2 mandava
verificar, e não presumir, se o `gate-rules.json` sofria do mesmo — e a
resposta foi NÃO. O parser do gate (`_le_registro`, Grupo 42) desfaz o
escape; o do `check-arch` (`_campos`, mais antigo) não. Assimetria entre
irmãos, de novo. Isso mudou o conserto: em vez de proibir, dar paridade.
Agora o `jq` usa `join("\t")` no lugar de `@tsv`, e o awk desfaz `\\`.

### O achado que ninguém procurava
Ao escrever o teste que força o caminho SEM jq, ele reprovou com
`awk: illegal statement`. **O fallback em awk do `check-arch.sh` nunca
funcionou** — usa `exp` como nome de variável, que é função embutida do awk.
Desde o Grupo 31, que o criou.

O efeito: em qualquer máquina sem `jq`, o runner imprimia
`check-arch: 0 regra(s), nenhuma violada` e saía 0. Verde total, zero regras
executadas. E o fallback existe exatamente para quem não tem jq — era essa
pessoa, e só ela, que recebia o falso verde.

Ninguém viu porque `jq` está instalado aqui e no CI: **o caminho que existe
para o ambiente que não temos era justamente o que nunca era exercitado.**
`tests/test_arch_rules.py` agora roda tudo nos dois caminhos, com um PATH
que tira `jq` e só ele.

### Também
- README da skill parou de anunciar o subagente de code review removido no
  Grupo 28 — pendência aberta desde então, baixada aqui.

## O que mudou nesta sessão (Grupo 44) — a skill rodada neste repositório
Pedido do usuário, para consertar por regeneração o `AGENTS.md` que estava
desatualizado. **O harness deste repositório foi trocado inteiro.**

O que entrou: `.cursor/hooks.json` (o Cursor rodava SEM enforcement nenhum
aqui), `registrar-sessao.sh`, `verificar-harness.sh`, `medir-aderencia.sh`,
`check-arch.sh`, `.harness/arch-rules.json` + `gate-rules.json`, o subagente
`propor-regra-arch`, a skill `executar-grupo`, o manifesto, e a ponte
`CLAUDE.md` que faltava ao lado do AGENTS.md com escopo — **a regra
inviolável nº 9 estava violada no próprio repo da skill**.

O gate instalado tinha 59 linhas e nenhuma `awk`: era anterior ao Grupo 6.
Isso explica os dois falsos bloqueios que aconteceram nesta sessão (um
scratchpad e uma mensagem de commit): já estavam corrigidos no Grupo 42, só
não aqui.

**Correção de premissa registrada:** o SESSION_STATE dizia que isto seria o
teste do catálogo `atualizacao.md`. NÃO FOI — `atualizacao.md` exige
`.claude/harness.json`, que não existia. O que a rodada exercitou foi a
FASE 3. E isso revelou um vão: repositório com harness ANTERIOR ao manifesto
não é geração limpa (os arquivos existem) nem atualização (não há manifesto),
e a skill não tem caminho para ele. Foi resolvido por decisão do usuário na
FASE 4, não por regra.

### Quatro defeitos da skill, três corrigidos
1. **`tests/test_skill.py` não fixava `HARNESS_GATE_RULES`** — o veredito
   dependia de o repositório onde o pytest roda ter um registro instalado.
   17 testes reprovaram ao instalar o harness. Eles nunca estiveram testando
   o que diziam; passavam por acidente de ambiente. E a expectativa estava
   velha: caminho temporário virou exceção no Grupo 42 e ninguém atualizou,
   justamente porque o fallback mascarava.
2. **`A04` sem a exclusão de `.claude/skills/`** que o `verificar-harness.sh`
   ganhou no Grupo 35 — a correção foi aplicada a uma das duas checagens
   irmãs e não à outra.
3. **`arch-rules.json` não carrega barra invertida no `check`**: o `@tsv` do
   jq re-escapa `\\` e o fallback em awk não desfaz. Descoberto ao tentar
   corrigir o defeito 2. Regra com `\\.` falha em silêncio — pior que não
   existir, porque parece que verifica. Documentado no próprio JSON.
4. **PENDÊNCIA — o verificador é cego para o repositório DA skill.** Acusa a
   fixture `com-preexistentes` (repo de ENTRADA: não ter ponte é o ponto
   dela) e marcadores em `tests/gerar.py`, `TASKS.md` e `evals/`, que
   legitimamente falam sobre eles. A exclusão do Grupo 35 cobre "skill
   instalada num alvo", não "este é o repo da skill". Fica em 9/11, e NÃO
   foi remendado: scanner ajustado para preservar a nota deixa de medir.

### Não feito, por regra da FASE 3
O CI existente não roda `bash .claude/check-arch.sh`, que agora faz parte da
DoD. A skill não edita pipeline existente — o step fica como sugestão,
registrado em `recusados` no manifesto.

## O que mudou nesta sessão (Grupo 43)
Dois defeitos do `medir-aderencia.sh`, os dois achados ao rodar o harness no
clone real do spring-petclinic depois do merge — mesma fonte de valor da
rodada anterior: repo de verdade encontra o que fixture não encontra.

1. **Alarme falso em repositório preexistente.** A medida 1 perguntava "que
   fração dos commits segue o protocolo?" e aplicava isso a commits feitos
   antes de o protocolo existir. A janela do `git log` passou a começar em
   `gerado_em`, e sem commit posterior à instalação a medida se declara cega
   — como a medida 5 já fazia. Eram duas medidas do mesmo script tratando a
   mesma situação de formas opostas; era isso que tornava o caso um defeito.
2. **SIGPIPE.** A causa não era óbvia: sem trap, o shell morre calado no
   `head`; é o `trap ... EXIT` do próprio script que o faz sobreviver, e aí
   o `printf` reporta. `trap '' PIPE` PIORA — testado.

Revalidado no PetClinic: **0 de 6 medidas em alerta** num harness
recém-instalado, contra 2 de 6 antes.

**Armadilha de método:** `tests/gerar.py` grava `gerado_em` com a constante
fixa `2026-07-27`, anterior ao commit do PetClinic. Com ela, o alerta
persistia mesmo com o conserto certo, e por um momento pareceu que a correção
não funcionava. Fixture com data congelada mede outra coisa que não a
realidade — vale para o próximo grupo que mexer em janela de tempo.

## O que mudou nesta sessão (Grupo 42)
Gate deixou de ser binário. `.harness/gate-rules.json` com `permitir` /
`bloquear` / `avisar`; exceções ancoradas em `^...$`; `avisar` grava `risco`
no trace e vira a medida 6 do `medir-aderencia.sh`; regras `G01`/`G02`
executam o gate na cadeia da DoD.

**A decisão de arquitetura foi do usuário**, apresentada com o contra: mover
padrões de segurança de código para dado permite ao agente editá-los. O
contra-argumento aceito foi que ele já podia editar o script, e que a defesa
real é a detecção na DoD, não o formato do arquivo.

**Prevenção onde é portátil, detecção onde não é.** O Cursor não tem evento
de pré-edição de arquivo (só `beforeReadFile` e `afterFileEdit`,
https://cursor.com/docs/hooks.md), então bloquear a edição do gate antes que
ela ocorra violaria a regra 10. Daí a G01.

**Interações que só apareceram rodando:**
- A sonda do `verificar-harness.sh` usava `/tmp/sonda-gate`, que virou
  exceção declarada. Uma exceção nova redefine o que as sondas antigas medem.
- O primeiro ataque testado (trocar todo `bloquear` por `permitir`) falha
  sozinho: sem regra de bloqueio, o gate cai no fallback. O ataque que
  funciona é manter os bloqueios e abrir uma exceção larga por cima.

## O que mudou nesta sessão (Grupo 41)
`registrar-sessao.sh`: hook de observação registrado nos três agentes, ao
lado do gate e nunca com `failClosed`. Grava uma linha por chamada de
ferramenta em `.harness/trace/`, com redação por lista de permissão. A medida
5 do `medir-aderencia.sh` lê esse trace e responde o que as medidas 1-4
declaravam não ver: sessão que editou arquivo e não commitou nada.

**Reduções de escopo declaradas, não silenciosas:**
- Contar bloqueios do gate ficou de fora. Exigiria o gate escrever em disco,
  e qualquer escrita dentro dele pode fazê-lo falhar aberto.
- O trace não vê raciocínio, custo, nem se a edição foi descartada depois.

**Dois defeitos achados pelos próprios testes**, ambos da mesma classe — os
dois lados escritos juntos, concordando por engano:
1. O teste de "sai 0 sempre" não mordia (a função interna já é total).
   Substituído por par comportamento + estrutura. `set -e` no hook quebraria
   o contrato sem nenhum teste de comportamento acusar.
2. O leitor da medida 5 quebrava com espaço depois dos dois-pontos e
   reportava "trace vazio" em vez de erro — quem lesse concluiria que não
   houve sessão.

## O que mudou nesta sessão (Grupo 40 + pesquisa)
Duas coisas, nesta ordem:

1. **`docs/` novo** — [harness-engineering.md](docs/harness-engineering.md)
   (pesquisa das fontes primárias: Böckeler/martinfowler, Anthropic, OpenAI,
   survey arXiv 2604.08224, awesome-list) e
   [intersecao-harness-engineering-x-skill.md](docs/intersecao-harness-engineering-x-skill.md)
   (42 características × o que a skill gera; placar 21 coberto / 8 parcial /
   2 proposto / 8 ausente / 3 fora de escopo, mais 6 lacunas priorizadas).
2. **Grupo 40** — `medir-aderencia.sh` no harness gerado.

**Correção registrada:** a lacuna 1 do doc de interseção estava larga demais
como escrita ("não há como medir se o harness melhora o comportamento"). É
falsa: este repo tem cinco níveis de eval (A/B em `eval/score-harness.sh`,
C em `eval/nivel-c/`, D em `evals/gradua.py`, E em `evals/triggering.json`).
A lacuna real é estreita — nenhum deles VIAJA com o harness; todos medem a
skill e rodam aqui. O Grupo 40 fecha só essa parte. **O doc ainda não foi
corrigido** para a forma estreita; está na lista de pendências.

**Achado do Grupo 40, medindo o próprio repositório:** a métrica de handoff
escrita como "SESSION_STATE no MESMO commit do checkpoint" dava 4 de 17 aqui.
Falso positivo — registrar o hash do checkpoint no arquivo obriga o commit
dele a existir antes. Aceitando também o commit seguinte: 17 de 17. O
medidor rodado contra este repo hoje dá 2 alertas de 4 (grupos concluídos
37 × 34 checkpoints, e 11 de 17 no handoff).
- Os três defeitos achados na rodada do PetClinic viraram os Grupos 34, 35 e
  36 — todos entregues. Rodar a skill num repo real pagou por si.
- Em andamento: nada — fronteira limpa.
- Não commitado: nada. O `-c` da raiz (lixo de execução manual antiga) foi
  apagado nesta sessão.
- Execução em série foi autorizada pelo usuário nesta sessão: a regra "PARE
  após o grupo" do AGENTS.md ficou suspensa, com push e relatório por grupo.

## O que mudou nesta sessão (Grupos 33, 31, 25, 29, 32 e 27)
Seis grupos entregues na `main`, CI verde em todos. Testes: 406 → 566.

- **33** — `format-on-edit.sh` era inerte em Java/Maven e Java/Gradle. Eram
  QUATRO defeitos encadeados: o template anexava `"$FILE_PATH"` no fim
  (Maven lê como fase de ciclo de vida e aborta); `gerar.py` preenchia
  `<formatter_command>` só com o binário, então nenhum teste exercitava o
  comando real; cabeçalho do hook e `ecossistemas.md` divergiam; e o stub
  rigoroso revelou que o hook checava `command -v gradle` mas rodava
  `./gradlew` — no-op em todo projeto com wrapper.
- **31** — a skill passou a gerar `.harness/arch-rules.json` e
  `.claude/check-arch.sh` na cadeia da DoD. `V6` saiu de `fail` para `pass`.
- **25** — gatilhos da `description` saíram de 47% para 10% do texto; TL;DR e
  duas duplicações removidas do corpo.
- **29** — FASE 1 passou a descobrir prefixo de branch e política de entrega
  por evidência (`git branch -r`, `git log --merges`, PULL_REQUEST_TEMPLATE,
  CODEOWNERS), não mais presumidos.
- **32** — agente `propor-regra-arch`, sem ferramenta de escrita: propõe
  regra, não veredito. Score voltou a +67.
- **27** — índice nos 8 arquivos longos, `compatibility`, `allowed-tools`.

## O que mudou nesta sessão (Grupo 28)
A skill deixou de gerar o subagente `code-reviewer`, a pedido do usuário. A
ressalva foi apresentada antes e mantida: na rodada do nível C o agente
delegava por conta própria (T1 e T2), e em T1 a revisão mudou o código.

O custo está medido e registrado, não maquiado: `V6 — Regras arquiteturais`
usava `.claude/agents/code-reviewer.md` como equivalência e passou de `eq` para
`fail`. O score da geração caiu de +64~+67 para **+62** em todos os
ecossistemas. `tests/fixtures/README.md` mostra as duas colunas lado a lado e
`eval/mapa-equivalencias.md` registra regra arquitetural como SEM COBERTURA. O
scanner **não** foi remendado para preservar a nota.

Efeito colateral que os sensores pegaram: o marcador `<checks-do-repo>` ficou
documentado sem template que o preenchesse, e os dois testes de marcador
reprovaram. Removido junto.

## O que mudou nesta sessão (Grupos 21, 22, 23 e 24)
Primeira execução do **nível C**, que existia só como protocolo em prosa
desde que foi escrito. Alvo: `spring-projects/spring-petclinic` (Java 17,
Maven, Spring Boot 4.1), duas cópias — uma com o harness gerado pela skill,
outra sem —, quatro tarefas por célula, `claude -p` headless rodando de
dentro de cada repo alvo.

- Resultado: falso "pronto" em **3 de 4** sessões sem harness contra **0 de
  4** com; 0 commits e build vermelho no controle contra 4 commits e build
  verde com harness; +65% de custo (US$ 1,94 → US$ 3,20).
- Relatório em `eval/nivel-c/petclinic-2026-07-28.md`, protocolo de execução
  em `eval/nivel-c/README.md`, JSONs brutos das 8 sessões em
  `eval/nivel-c/runs/`.
- A bateria virou reexecutável: `preparar.sh` (painel + baseline), `roda.sh`
  (uma célula, com o bug plantado e a DoD medida DEPOIS da sessão),
  `tarefas.json` (T1–T4 com prompt literal) e `mede.py` (tabela comparativa).
  Comando `/exp-nivel-c` amarra os quatro. `pyproject.toml` passou a incluir
  `eval` no mypy.
- Dois defeitos do `mede.py` apareceram ao rodá-lo sobre os dados reais e
  foram corrigidos com teste: DoD não medida contava como verde (`0 de 4` lido
  como quatro sessões boas), e o commit de instalação do harness inflava a
  contagem de commits da célula `harness` em um.
- O `README.md` da raiz ganhou a seção "Isso funciona?" com o placar da
  rodada, e um teste que reprova se algum número dela não existir no
  relatório — a vitrine não anda sozinha.

## Execução real da skill no Spring PetClinic (2026-07-29)
Rodada de validação a pedido do usuário, num clone de
`spring-projects/spring-petclinic` (`f182358`, Java 17, Maven+Gradle).

- Resultado: **L0 · 39/108 -> L4 · 89/108**. Verificador 11/11, check-arch
  5/5, gate provado (exit 2 no destrutivo, 0 na DoD).
- Executada pelo próprio agente da sessão, não headless: o
  `claude -p --permission-mode bypassPermissions` foi bloqueado pelo
  classificador. **A medição é fraca** — quem executou escreveu a skill nesta
  mesma sessão, que é exatamente o viés que o `evals/README.md` alerta.
- A geração legítima ali é SEM `format-on-edit.sh`: o PetClinic usa
  `spring-javaformat`, que não escopa por arquivo.
- Três defeitos da skill apareceram. Um virou o Grupo 34 (já entregue); os
  outros dois viraram os Grupos 35 e 36.
- Alvo em `<scratchpad>/javatest/alvo` — some com a sessão; a rodada é
  reproduzível pelos passos acima.

## Integração com OpenSpec — provada de ponta a ponta (2026-07-29)
Verificada contra o CLI real: `npx @fission-ai/openspec@latest`, versão 1.7.0
([Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)).

- A ferramenta LÊ o `openspec/config.yaml` gerado: corrompendo-o de propósito,
  o `doctor` avisa `could not parse ...; ignoring it`; com o gerado, silêncio.
- `openspec validate --all` na fixture: `1 passed, 0 failed`.
- O validador exige estrutura em INGLÊS (`## Why`, `## What Changes`,
  `MUST`/`SHALL`) mesmo com conteúdo em português — registrado na FASE 1.
- Instalação global do CLI falhou por permissão nesta máquina; tudo foi feito
  via `npx`. Se quiser o binário fixo: `npm install -g @fission-ai/openspec`.

## Validação no spring-petclinic real (2026-07-30, após o merge)
Clone raso de `spring-projects/spring-petclinic` (`88e37c1`), harness gerado
por `tests/gerar.py`. **Ressalva de método:** é a reimplementação
determinística da FASE 2, não a skill executada por um modelo — o nível D
existe para medir essa diferença. E **não há JDK nesta máquina** (Maven sim,
runtime não), então o build do PetClinic não foi executado; o que foi
validado é a maquinaria do harness, que é toda shell.

Resultado: verificador **11/11**; check-arch **7/7** incluindo as regras
`G01`/`G02` novas; gate graduado correto contra caminhos reais (`target` e
`build` liberados, `src/main/java` e `/` bloqueados, e a exceção não abriu
buraco em `target && /`); trace classificando risco; e a senha de teste
`SPRING_DATASOURCE_PASSWORD=s3nh4-real` **não chegou ao disco**. Geração sem
`format-on-edit.sh`, que é o correto para `spring-javaformat`.

### DEFEITO ENCONTRADO E CORRIGIDO no Grupo 43 — medida 1 alarme falso
Num repositório que acabou de receber o harness, TODO o histórico é anterior
a ele e portanto não tem como conter commits `checkpoint:`. A medida 1
reporta **0% e ALERTA**, acusando o time de indisciplina por um período em
que o protocolo não existia.

É a mesma classe de problema que a medida 5 já trata bem (sem trace, ela se
declara cega em vez de alertar) e exatamente o modo de falha contra o qual o
próprio Grupo 42 argumenta: alarme falso é o que faz o sensor ser ignorado.

**Corrigido no Grupo 43**: a janela do `git log` passou a começar em
`gerado_em`, e sem commit posterior à instalação a medida se declara cega.
Revalidado no PetClinic: **0 de 6 medidas em alerta**, contra 2 de 6 antes.

Armadilha de método que quase escondeu o conserto: `tests/gerar.py` grava
`gerado_em` com a constante fixa `2026-07-27`, anterior ao commit do
PetClinic. Com ela o alerta persistia mesmo com a correção certa. Fixture com
data congelada mede outra coisa que não a realidade.

### Defeito menor, também corrigido no Grupo 43
`printf: write error: Broken pipe` no stderr ao truncar com `head`. A causa
não era óbvia: sem trap o shell morre calado; é o `trap ... EXIT` do próprio
script que o faz sobreviver ao SIGPIPE, e aí o printf reporta. E `trap '' PIPE`
PIORA — produz o erro em vez de evitá-lo.

## Pendências
- **A seção "Fontes de trabalho" do AGENTS.md gerado nomeia
  `openspec/changes/<change-ativa>/tasks.md` mesmo em repo sem `openspec/`.**
  Achado ao escrever o sensor do Grupo 51 (`resources/AGENTS.md:11`). Não é a
  falha do comando inexistente — não manda CHAMAR nada, só lista as fontes
  possíveis do protocolo —, mas nomeia um caminho que não existe ali, e um
  agente pode criar a pasta achando que é fonte válida. Fora do escopo do 51.
  O Grupo 52 reescreve exatamente essa seção: é lá que se decide se a lista
  passa a ser condicional.
- **`/opsx:propose` e `/opsx:apply` no AGENTS.md gerado são nomes de
  comando do Claude Code, e o harness vale em três agentes.** Descoberto ao
  fechar o Grupo 48, ao provar o nome do explore: no Cursor o comando é
  `opsx-propose` e no Devin é `.devin/workflows/opsx-propose.md`, enquanto as
  skills (`openspec-propose`, `openspec-apply-change`) têm o mesmo nome nos
  três. O texto do explore já usa a forma invariante; o de propose/apply não
  foi tocado (fora do escopo do grupo, WIP=1).
- **O harness DESTE repositório ficou atrás do produto (Grupo 47).** O
  `AGENTS.md` da raiz ainda diz "Fontes de trabalho (nesta ordem de
  precedência) — use o primeiro que existir", e o `.claude/skills/
  executar-grupo/SKILL.md` ainda escolhe a fonte por ordem de arquivo. O
  template já mudou; este repo não foi regenerado (fora do escopo do grupo,
  WIP=1). Enquanto isso não for feito, o repositório que constrói o gerador
  segue uma regra que o gerador não ensina mais. Reconfirmado em 2026-08-27 ao planejar o Grupo 52: as duas cópias divergem no passo 3 — a deste repo escolhe por ordem de arquivo, o template pergunta quando as duas fontes têm grupo aberto. Como o 52.3 mexe nesse mesmo passo, é o momento natural de regenerar.
- **A lacuna 2 do doc de interseção foi CANCELADA, não implementada.** Era
  erro de documentação: `propor-regra-arch` já é um controle inferencial
  gerado, e o revisor com veredito foi removido no Grupo 28 por decisão do
  usuário, com custo medido. Reclassificada como "Fora de escopo (decisão
  explícita)" no commit `2e559ed`. Resíduo real e NÃO tratado: a camada
  inferencial vale só para Claude Code, porque a doc do Devin não publica os
  paths de subagente.
- **Conferir as 6 linhas ainda marcadas "Ausente" no doc de interseção**
  contra `eval/`, `evals/` e o histórico do `TASKS.md` antes de virarem
  plano. As duas que já viraram estavam erradas pelo mesmo motivo: foram
  escritas olhando só o repo alvo e o `resources/` da skill.
- **BLOQUEADOR: o instrumento do nível E não detecta disparo nenhum.** Teste
  de sanidade: skill `deploy-producao`, description "Use SEMPRE que o usuario
  pedir para rodar o deploy de producao", query "roda o deploy de producao
  pra mim agora" → `trigger_rate 0.00`. O `run_eval.py` cria o command file e
  o `claude -p` responde; a detecção é que nunca acende, provavelmente por
  formato de evento do `stream-json` que mudou de versão. **Consequência:** o
  "subdisparo" medido no nível E pode ser artefato, e a conclusão de que ele
  "não se resolve reescrevendo a description" precisa ser reaberta. O Grupo
  26 está bloqueado por isto. Registrado em `evals/README.md`.
- O nível C ficou em **n=1 por célula**; o protocolo pede 3. Subir para 3 é o
  próximo passo antes de tratar qualquer número como estável.
- **O `AGENTS.md` deste repo está desatualizado em dois pontos, e a causa é
  uma só: ele foi escrito à mão e nunca regenerado.** Manda
  `git checkout develop` (a skill corrigiu isso no Grupo 7.1 com
  `<branch-base>` descoberto por git) e cita `/opsx:propose` sem haver
  `openspec/` (corrigido no 7.2 com `<como-propor-mudanca-de-plano>`). O
  terceiro item, o `code-reviewer` órfão, saiu no Grupo 30. A correção mais
  barata talvez não seja editar à mão de novo, e sim rodar a própria skill
  neste repositório — que é também o teste real do catálogo `atualizacao.md`,
  hoje exercitado só por fixture.
- **Descoberta da FASE 1 como script bundled — decisão de design em aberto.**
  O `skill-creator` oficial manda procurar trabalho que se repete a cada
  invocação e empacotá-lo em `scripts/`; a FASE 1 refaz a investigação de
  stack/comandos/lockfile à mão toda vez, e este repo já tem o código que faz
  isso programaticamente (`tests/gerar.py`). Não virou task: trocar raciocínio
  por script muda o que a skill é, e o ganho precisa ser medido (custo e
  variância entre execuções) antes de valer um grupo.
- Herdadas das sessões anteriores: subdisparo da skill (nível E) não se
  resolve reescrevendo a `description`; iteração 2 do nível D por fazer;
  Grupo 17 por escrever; o `AGENTS.md` deste repo ainda manda
  `git checkout develop` (só existe `main`) e citar `/opsx:propose` (não há
  `openspec/`).
- Próxima ação: `git push origin main` (não feito — ninguém pediu para
  publicar). Depois, a rodada com n=3 usando o `/exp-nivel-c`, ou o grupo de
  correção do `format-on-edit.sh` em Java.
