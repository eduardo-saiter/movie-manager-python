# 🎬 Movie Manager

A command-line application built with Python to search, save, rate, comment on, and manage movies.

The application searches the local SQLite catalog first. When a movie is not stored locally, it queries the OMDb API and allows the user to save the result.

This project was created to practice object-oriented programming, layered architecture, dependency injection, REST API consumption, SQLite persistence, exception handling, environment variables, and automated testing.

---

## ✨ Features

- Search movies by title
- Search the local SQLite catalog before accessing the API
- Retrieve movie information from the OMDb API
- Save movies in a local database
- List saved movies
- Rate movies from 0 to 5 stars
- Add and update personal comments
- Update movie ratings
- Delete saved movies
- Handle empty titles, unavailable movies, timeouts, connection failures, and HTTP errors
- Store the OMDb API key in an environment variable

---

## 🔎 Application flow

```text
User enters a movie title
          │
          ▼
Search local SQLite database
          │
     ┌────┴────┐
     │         │
  Found     Not found
     │         │
     ▼         ▼
Display     Search OMDb API
movie           │
                ▼
             Display movie
                │
                ▼
          Ask whether to save
                │
                ▼
       Rating + optional comment
```

---

## 🛠️ Technologies

- Python 3
- SQLite3
- Requests
- python-dotenv
- Pytest

---

## 🧱 Architecture

The project separates user interaction, business rules, external API communication, and database access.

```text
main.py
   │
   ▼
MovieServices
   ├── MovieApiClient ──► OMDb API
   │
   └── MovieRepository ──► SQLite
                │
                ▼
              Movie
```

### Responsibilities

- **`main.py`** — controls the command-line interface and user input
- **`MovieServices`** — coordinates business rules and application behavior
- **`MovieApiClient`** — communicates with the OMDb API
- **`MovieRepository`** — reads and writes movie data in SQLite
- **`database.py`** — creates the database connection and initializes the schema
- **`Movie`** — represents a movie inside the application
- **`exhibition.py`** — displays the menu and movie information

---

## 📁 Project structure

```text
movie-manager-python/
│
├── clients/
│   └── movie_api_client.py
│
├── database/
│   └── database.py
│
├── models/
│   └── movie.py
│
├── repositories/
│   └── movies_repository.py
│
├── services/
│   └── movie_services.py
│
├── tests/
│   ├── conftest.py
│   ├── test_movie_api_client.py
│   ├── test_movie_services.py
│   └── test_movies_repository.py
│
├── utils/
│   └── exhibition.py
│
├── main.py
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── LICENSE
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone git@github.com:eduardo-saiter/movie-manager-python.git
cd movie-manager-python
```

You can also clone it with HTTPS:

```bash
git clone https://github.com/eduardo-saiter/movie-manager-python.git
cd movie-manager-python
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install the application dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the OMDb API key

Create a `.env` file in the project root:

```env
OMDB_API_KEY=your_api_key
```

The `.env` file is ignored by Git and must not be committed.

### 6. Run the application

```bash
python main.py
```

The SQLite database is created automatically inside the `database/` directory when the application starts.

---

## 🖥️ Menu

```text
=== Movie Manager ===
1. Search movie
2. List Saved Movies
3. Update Movie Review
4. Update Movie Comment
5. Delete Movie
6. Exit
```

---

## 🧪 Tests

Install the development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the test suite:

```bash
pytest -v
```

The tests use mocks and an isolated SQLite database so they do not need to access the real OMDb API or the application's main database.

> The test suite is being updated as the database features and business rules evolve.

---

## 🗺️ Roadmap

- [x] Search movies through the OMDb API
- [x] Handle API and connection errors
- [x] Add SQLite persistence
- [x] Search the local database before the API
- [x] Save and list movies
- [x] Add ratings from 0 to 5
- [x] Add personal comments
- [x] Update ratings and comments
- [x] Delete saved movies
- [ ] Finish updating tests for the current features
- [ ] Prevent duplicate movie records
- [ ] Improve input validation and menu messages
- [ ] Add movie search history

---

## 📚 Concepts practiced

- Object-oriented programming
- Dataclasses
- Layered architecture
- Separation of concerns
- Dependency injection
- Repository pattern
- Service layer
- REST API consumption
- HTTP requests and responses
- Environment variables
- SQLite and CRUD operations
- Exception handling
- Unit testing, fixtures, mocks, and monkeypatch

---

## 📄 License

This project is licensed under the MIT License.
