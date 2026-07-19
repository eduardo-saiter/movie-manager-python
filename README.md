# 🎬 Movie Manager

A command-line application developed in Python to search for movie information using the OMDb API.

This project was created to practice object-oriented programming, layered architecture, REST API consumption, environment variables and automated testing.

---

## Features

- Search movies by title
- Display movie information
- Consume data from the OMDb API
- Handle invalid titles
- Handle connection errors

---

## Technologies

- Python 3
- Requests
- python-dotenv
- Pytest

---

## Project structure

```text
movie-manager-python/
│
├── clients/
├── models/
├── services/
├── utils/
├── tests/
│
├── main.py
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── LICENSE
```

---

## Architecture

```text
User
 │
 ▼
main.py
 │
 ▼
MovieService
 │
 ▼
MovieApiClient
 │
 ▼
OMDb API
 │
 ▼
Movie
```

### Responsibilities

- **main.py** → user interaction
- **MovieService** → business rules
- **MovieApiClient** → communication with the OMDb API
- **Movie** → movie representation

---

## Installation

Clone the repository:

```bash
git clone https://github.com/eduardo-saiter/movie-manager-python.git
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

Linux/macOS

```bash
source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```text
OMDB_API_KEY=your_api_key
```

Run the application:

```bash
python main.py
```

---

## Tests

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run:

```bash
pytest
```

---

## Roadmap

- [x] Search movies by title
- [x] Consume REST API
- [ ] SQLite persistence
- [ ] Favorite movies
- [ ] Movie ratings
- [ ] Search history
- [ ] Complete automated test coverage

---

## License

This project is licensed under the MIT License.