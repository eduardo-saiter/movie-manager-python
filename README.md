# 🎬 Movie Manager

Movie Manager is a Python application for searching, saving, rating, commenting on, and organizing movies.

The project provides two interfaces over the same application logic:

- a **local web application** built with FastAPI, Jinja2, HTML, and CSS;
- a **command-line interface** for terminal use.

When a title is searched, the application combines partial matches from the local SQLite catalog with the OMDb search results. Items already saved are identified by their IMDb ID and open the local detail page; external results open an OMDb detail page and can then be added to the catalog.

The project was developed to practice object-oriented programming, layered architecture, external API consumption, SQLite persistence, validation, automated testing, and web development with Python.

---

## ✨ Features

- Search partial movie titles in the local catalog
- Combine local matches with OMDb search results
- Detect OMDb results that are already saved and open their local record
- Save API results in SQLite
- Display movie posters
- List saved movies in a responsive card grid
- Open movie details by clicking the poster
- Rate movies from 0 to 5 stars
- Add and update personal comments
- Delete movies from the catalog
- Prevent duplicate IMDb IDs with a case-insensitive database `UNIQUE` constraint
- Validate empty searches, ratings, comments, and missing movie IDs
- Display user-friendly error messages
- Handle API timeouts, connection failures, and database errors
- Use the same service and repository layers in both the web and terminal interfaces

---

## 🔎 Search flow

```text
User searches for part of a title
             │
       ┌─────┴─────┐
       ▼           ▼
Local SQLite    OMDb search
results         results
       └─────┬─────┘
             ▼
Merge by IMDb ID and remove duplicates
             │
       ┌─────┴─────┐
       ▼           ▼
Saved item     External item
/movies/{id}   /omdb/{imdb_id}
```

---

## 🧱 Architecture

The project separates HTTP routes, application rules, persistence, API communication, and presentation.

```text
Browser
   │
   ▼
FastAPI application
web_app.py
   │
   ▼
APIRouter / route controllers
routers/movie_router.py
   │
   ▼
MovieServices
   ├────────► MovieApiClient ─────► OMDb API
   │
   └────────► MovieRepository ────► SQLite
                     │
                     ▼
                   Movie
```

The terminal interface also uses the same service layer:

```text
main.py ─────► MovieServices ─────► Repository / API client
```

### Main responsibilities

| Component | Responsibility |
|---|---|
| `web_app.py` | Creates and configures the FastAPI application |
| `routers/movie_router.py` | Defines web routes and handles HTTP requests and responses |
| `web_dependencies.py` | Creates the templates, database connection, repository, API client, and service |
| `services/movie_services.py` | Applies validation and coordinates application rules |
| `repositories/movies_repository.py` | Performs SQLite CRUD operations |
| `clients/movie_api_client.py` | Communicates with the OMDb API |
| `database/database.py` | Creates the SQLite connection and initializes the schema |
| `models/` | Defines `Media`, `Movie`, future series/episode models, search results, and external ratings |
| `mappers/omdb_mapper.py` | Converts raw OMDb payloads into application models |
| `templates/` | Contains the Jinja2 HTML pages |
| `static/` | Contains the CSS styles |
| `utils/exhibition.py` | Formats output for the terminal interface |

---

## 🛠️ Technologies

- Python 3.10+
- FastAPI
- Uvicorn
- Jinja2
- HTML and CSS
- SQLite
- Requests
- python-dotenv
- Pytest

---

## 📁 Project structure

```text
movie-manager-python/
├── clients/
│   └── movie_api_client.py
├── database/
│   └── database.py
├── mappers/
│   └── omdb_mapper.py
├── models/
│   ├── media.py
│   ├── movie.py
│   ├── media_search_result.py
│   └── external_rating.py
├── repositories/
│   └── movies_repository.py
├── routers/
│   └── movie_router.py
├── services/
│   └── movie_services.py
├── static/
│   └── styles.css
├── templates/
│   ├── index.html
│   ├── search_results.html
│   └── details_data.html
├── tests/
│   ├── conftest.py
│   ├── test_database.py
│   ├── test_exhibition.py
│   ├── test_main.py
│   ├── test_movie_api_client.py
│   ├── test_movie_services.py
│   ├── test_movies_repository.py
│   └── test_web_app.py
├── utils/
│   └── exhibition.py
├── main.py
├── web_app.py
├── web_dependencies.py
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── LICENSE
```

---

## 🚀 Installation

### 1. Clone the repository

Using SSH:

```bash
git clone git@github.com:eduardo-saiter/movie-manager-python.git
cd movie-manager-python
```

Using HTTPS:

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

### 4. Install the dependencies

Application dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Development and test dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

### 5. Configure the OMDb API key

Create a `.env` file in the project root:

```env
OMDB_API_KEY=your_api_key
```

The `.env` file is ignored by Git and must not be committed.

---

## 🌐 Run the web application

Start the development server:

```bash
python -m fastapi dev web_app.py
```

Open the application in the browser:

```text
Application: http://127.0.0.1:8000
API docs:    http://127.0.0.1:8000/docs
```

### Access from another device on the same local network

Start Uvicorn on all network interfaces:

```bash
python -m uvicorn web_app:app --host 0.0.0.0 --port 8000
```

Find the computer's local IP address on Linux:

```bash
hostname -I
```

Then open the following address on another device connected to the same network:

```text
http://YOUR_LOCAL_IP:8000
```

The current application has no authentication and is intended for local development. Do not expose it directly to an untrusted public network.

---

## 💻 Run the command-line application

```bash
python main.py
```

The SQLite database is created automatically inside the `database/` directory.

---

## 🛣️ Main web routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/` | Display the saved movie catalog |
| `GET` | `/search?title=...` | Combine partial local and OMDb search results |
| `GET` | `/omdb/{imdb_id}` | Display complete details for an OMDb result |
| `POST` | `/movies/save` | Save a movie returned by the API |
| `GET` | `/movies/{movie_id}` | Display a saved movie by ID |
| `POST` | `/movies/{movie_id}/update-rating` | Update a movie rating |
| `POST` | `/movies/{movie_id}/update-comment` | Update a personal comment |
| `POST` | `/movies/{movie_id}/delete-movie` | Delete a saved movie |

---

## ✅ Validation and error handling

The service layer validates application data before calling the repository.

Examples:

- movie titles cannot be empty;
- ratings must be integers between 0 and 5;
- comments cannot be empty or longer than 500 characters;
- operations using an unknown movie ID are rejected;
- duplicate IMDb IDs are blocked by SQLite;
- OMDb timeouts and connection errors are converted into user-friendly messages;
- the web routes return appropriate HTTP status codes such as `400`, `404`, and `503`.

---

## 🧪 Tests

The project currently contains **123 automated test cases**.

Run the full suite:

```bash
pytest -q
```

Check which tests will be collected:

```bash
pytest --collect-only -q
```

Current result:

```text
123 passed
```

The tests cover:

- database initialization and constraints;
- OMDb client behavior without real network requests;
- SQLite repository operations using an in-memory database;
- service rules and validation;
- web routes, forms, redirects, templates, and HTTP status codes;
- terminal output and shutdown behavior.

Mocks and an isolated in-memory SQLite database keep the test suite independent from the real OMDb API and the local application database.

---

## 📚 Concepts practiced

- Object-oriented programming
- Dataclasses
- Type hints
- Layered architecture
- Separation of concerns
- Repository pattern
- Service layer
- Router/controller organization
- Dependency composition
- REST API consumption
- HTTP methods and status codes
- FastAPI forms and path/query parameters
- Jinja2 templates
- HTML and CSS
- Environment variables
- SQLite CRUD operations
- Validation and exception handling
- Pytest fixtures, mocks, monkeypatch, and parametrization

---

## 🗺️ Possible next steps

- [x] Use FastAPI `Depends()` for dependency injection in the routers
- [x] Create a dedicated movie-detail template
- [x] Use the OMDb/IMDb identifier as the primary uniqueness rule
- [ ] Add database migrations
- [ ] Improve accessibility and responsive styling
- [ ] Add pagination and catalog filters
- [ ] Add authentication before any public deployment

---

## 📄 License

This project is distributed under the terms described in the [LICENSE](LICENSE) file.
