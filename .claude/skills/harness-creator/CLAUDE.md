<!-- Ponte para o Claude Code, que carrega CLAUDE.md e NAO carrega AGENTS.md.
     O `@` importa o arquivo irmao no inicio da sessao, entao o conteudo vive
     num lugar so: os demais agentes leem o AGENTS.md direto, o Claude Code
     chega nele por aqui. Sem esta ponte, o protocolo (DoD, WIP=1, MUST NOT)
     nao entra no contexto do Claude Code e o harness vira documentacao.
     Comentarios de bloco sao removidos antes de o arquivo entrar no contexto,
     entao este texto nao custa token nenhum.
     Instrucoes especificas do Claude Code, se houver, vao ABAIXO do import. -->
@AGENTS.md
