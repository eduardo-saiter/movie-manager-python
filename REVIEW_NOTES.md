# Revisão funcional — 05/08/2026

## Correções principais

- Atualização completa dos testes para o esquema atual (`media`,
  `movie_details` e `external_ratings`).
- Salvamento de filme tornado atômico: uma falha em qualquer avaliação externa
  desfaz toda a transação e não deixa IDs falsos nos objetos.
- Busca local agora remove espaços nas extremidades e mantém comparação sem
  diferença entre maiúsculas e minúsculas.
- Resultados locais e da OMDb são unidos sem duplicar a mesma mídia.
- Um resultado da OMDb já salvo recebe o `local_id` e abre a página local.
- Registros antigos sem `imdb_id` também são reconhecidos pelo título e ano.
- Restrição case-insensitive para IMDb ID aplicada também a bancos já criados,
  por meio de índice único.
- Chaves estrangeiras são ativadas também durante a inicialização do banco,
  garantindo o funcionamento do `ON DELETE CASCADE` em testes e conexões novas.
- Validações de título, IMDb ID, avaliação e comentário foram alinhadas entre
  web e terminal.
- Erros internos do SQLite não são mais expostos nas páginas.
- Rotas de atualização e exclusão agora tratam falhas de banco com status 503.
- Formulários deixaram de enviar o campo oculto `title`, que não era utilizado.
- Correção da exibição de duração ausente (`Não informado`, sem `min` sobrando).
- Correção do `except` genérico no terminal para não capturar interrupções do
  usuário.
- Cliente OMDb passou a solicitar explicitamente filmes e sinopse completa.
- Arquivo de teste manual antigo removido e `.env.example` adicionado.

## Testes

A suíte final possui **123 testes**, incluindo um teste de integração que cobre:

```text
busca OMDb → detalhes → salvar → busca local → avaliar → comentar → excluir
```

Resultado verificado:

```text
123 passed
```

Também foram executados `compileall`, teste de importação e smoke test da página
inicial.
