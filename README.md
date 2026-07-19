# 🎬 Movie Manager

Um gerenciador de filmes desenvolvido em Python que consome uma API REST para pesquisar filmes e permite salvar seus favoritos em um banco de dados SQLite.

O projeto tem como objetivo praticar conceitos importantes de desenvolvimento de software, como Programação Orientada a Objetos, arquitetura em camadas, consumo de APIs, persistência de dados e testes automatizados.

---

## ✨ Funcionalidades

- Pesquisar filmes por título
- Visualizar informações detalhadas
- Salvar filmes favoritos
- Listar filmes favoritos
- Remover filmes favoritos
- Avaliar filmes salvos
- Persistência utilizando SQLite

---

## 🛠 Tecnologias

- Python 3
- SQLite
- Requests
- Pytest

---

## 📁 Estrutura do projeto

```text
movie-manager-python/
│
├── clients/
├── database/
├── models/
├── repositories/
├── services/
├── tests/
│
├── main.py
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── LICENSE
```

---

## 🏗 Arquitetura

O projeto utiliza uma arquitetura em camadas.

```
Usuário
    │
    ▼
main.py
    │
    ▼
MovieService
    │
    ├────────────► MovieApiClient
    │
    ▼
MovieRepository
    │
    ▼
SQLite
```

Cada camada possui uma responsabilidade específica.

- **main.py**: interação com o usuário.
- **Service**: regras de negócio.
- **Repository**: acesso ao banco de dados.
- **API Client**: comunicação com a API de filmes.
- **Model**: representação dos objetos.

---

## 🚀 Como executar

Clone o repositório:

```bash
git clone https://github.com/eduardo-saiter/movie-manager-python.git
```

Entre na pasta:

```bash
cd movie-manager-python
```

Crie um ambiente virtual:

```bash
python3 -m venv .venv
```

Ative o ambiente:

Linux/macOS

```bash
source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute:

```bash
python main.py
```

---

## 🧪 Testes

Instale as dependências de desenvolvimento:

```bash
pip install -r requirements-dev.txt
```

Execute todos os testes:

```bash
pytest
```

---

## 📈 Roadmap

- [ ] Buscar filmes por título
- [ ] Consumir API REST
- [ ] Salvar favoritos
- [ ] Sistema de avaliações
- [ ] Pesquisa por gênero
- [ ] Pesquisa por ator
- [ ] Histórico de pesquisas
- [ ] Cobertura completa de testes
- [ ] Interface gráfica ou Web

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT.