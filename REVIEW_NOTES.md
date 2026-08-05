# Revisão técnica do projeto

Revisão realizada em 05/08/2026 sobre a versão completa do Movie Manager.

## Validações executadas

- suíte automatizada completa;
- cobertura de testes;
- compilação de todos os arquivos Python;
- parsing dos templates Jinja2;
- parsing do CSS;
- comparação entre classes usadas no HTML e classes definidas no CSS;
- inicialização do site sem arquivo `.env`;
- integridade e chaves estrangeiras do banco SQLite existente;
- fluxo integrado de busca, detalhes, salvamento, atualização e exclusão.

## Resultado

```text
153 passed
Cobertura aproximada do código da aplicação: 82%
SQLite integrity_check: ok
Erros de parsing CSS: 0
Erros de parsing Jinja2: 0
```

## Correções aplicadas

- exibição do erro de banco na página inicial;
- validação amigável de formulários vazios, sem respostas JSON 422 nos fluxos normais;
- status HTTP `404` para operações em filmes inexistentes e `409` para duplicidade;
- redirects gerados pelos nomes das rotas, sem caminhos fixos;
- cliente OMDb inicializável sem chave, permitindo abrir o catálogo local;
- mensagem `503` quando uma busca externa é tentada sem chave configurada;
- validação de respostas JSON inválidas da OMDb;
- exigência de IMDb ID para filmes retornados e salvos;
- remoção de avaliações externas duplicadas pelo nome da fonte;
- validação de título, avaliação e comentário antes do salvamento;
- busca SQLite tratando `%`, `_` e `\\` como texto literal;
- conexão SQLite com timeout e `busy_timeout`;
- campos essenciais de mídia marcados como `NOT NULL` em bancos novos;
- placeholder para pôster ausente na página de detalhes;
- limpeza e simplificação do `.gitignore`;
- criação de `.env.example`;
- atualização da documentação e das dependências de desenvolvimento;
- remoção de inconsistências da interface de terminal.

A cobertura não inclui os próprios arquivos de teste. O percentual total é
reduzido principalmente pela interface de terminal e pelos modelos futuros de
séries e episódios, enquanto as camadas web, repository, service e cliente da
OMDb possuem cobertura mais alta.

## Limitações conhecidas

Estas limitações não impedem o funcionamento atual, mas são bons próximos passos:

1. **Migrações de banco:** `CREATE TABLE IF NOT EXISTS` não altera tabelas antigas. Mudanças futuras de esquema devem usar uma ferramenta ou sistema de migração.
2. **Séries e episódios:** os modelos e tabelas existem, mas ainda não possuem repository, service, rotas e interface próprios.
3. **Paginação:** a busca usa a primeira página retornada pela OMDb.
4. **Desempenho do catálogo:** a listagem carrega avaliações externas com uma consulta adicional por filme. Isso é aceitável para um catálogo pequeno, mas pode ser otimizado para muitos registros.
5. **Segurança pública:** o projeto não possui autenticação nem proteção CSRF. Ele deve continuar restrito ao uso local até essas camadas serem implementadas.
6. **Formatação regional:** datas, votos e bilheteria ainda podem ganhar filtros Jinja2 para apresentação em formato brasileiro.
7. **Interface de terminal:** funciona, mas possui menos testes de fluxo do que a aplicação web.
