# Testes

A suíte usa `pytest`, banco SQLite em memória e mocks. Nenhum teste faz uma
requisição real à OMDb nem altera o banco local do projeto.

## Executar

```bash
pytest -q
```

Resultado atual:

```text
123 passed
```

## Organização

- `test_database.py`: criação do esquema, restrições, chaves estrangeiras,
  `CASCADE` e atualização de timestamp.
- `test_omdb_mapper.py`: conversão dos payloads da OMDb para os modelos.
- `test_movie_api_client.py`: cliente HTTP da OMDb, sem usar a internet.
- `test_movies_repository.py`: transações, CRUD, buscas e avaliações externas
  no SQLite em memória.
- `test_movie_services.py`: regras, validações, união de resultados locais e
  externos e conversão de erros.
- `test_web_app.py`: rotas FastAPI, formulários, redirects, templates e status
  HTTP.
- `test_integration_flow.py`: fluxo web completo da busca na OMDb até a exclusão.
- `test_exhibition.py`: apresentação da versão de terminal.
- `test_main.py`: encerramento seguro da aplicação de terminal.
