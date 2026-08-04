# Testes

A suíte usa `pytest`, banco SQLite em memória e mocks. Nenhum teste faz uma
requisição real à OMDb nem altera o banco local do projeto.

## Executar

```bash
pytest -q
```

## Executar com cobertura das camadas principais

```bash
pytest \
  --cov=clients \
  --cov=database \
  --cov=models \
  --cov=repositories \
  --cov=routers \
  --cov=services \
  --cov=utils \
  --cov=web_app \
  --cov=web_dependencies \
  --cov-report=term-missing
```

## Organização

- `test_database.py`: criação e restrições da tabela.
- `test_movie_api_client.py`: cliente HTTP da OMDb, sem usar a internet.
- `test_movies_repository.py`: persistência no SQLite em memória.
- `test_movie_services.py`: regras, validações e conversão de erros.
- `test_web_app.py`: rotas FastAPI, formulários, redirects e status HTTP.
- `test_exhibition.py`: apresentação da versão de terminal.
- `test_main.py`: encerramento seguro da aplicação de terminal.
