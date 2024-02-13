![python-badge](https://img.shields.io/badge/Python-3.9+-blue) ![license-badge](https://img.shields.io/badge/License-MIT-blue) 

# TaskifyAPI
An API using FastAPI and PostgreSQL to create, share or keep track of tasks. This project also has a CRUD System Using JWT and Oauth2 to Create a Complete API that can be used with a frontend project

## Getting Started

### Prerequisites

- Python 3.9 or higher

### Project setup

```sh
# clone the repo (...or download in releases)
$ git clone https://github.com/pluresque/taskify-api.git

# move to the project folder
$ cd taskify-api
```

### Configuring Environment

```sh
# rename .env.dist to .env
$ mv .env.dist .env
```
Replace the values in the `.env` file with your own values.

### Running in a container

```sh
$ docker-compose up
```

### Running locally

```sh
# Install dependencies
$ pip install -e . 

# Load inital data (if needed)
$ python3 src/scripts/bootstrap.py

# Start the FastAPI server
$ uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Packages
| Package                                                         | Usage                                                                                                                      |
|-----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| [uvicorn](https://github.com/encode/uvicorn)                    | a lightning-fast ASGI server implementation, using uvloop and httptools.                                                   |
| [FastAPI](https://github.com/tiangolo/fastapi)                  | a modern, fast (high-performance), web framework for building APIs based on standard Python type hints                     |
| [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy)          | a Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL. |
| [starlette](https://www.starlette.io/)                          | a lightweight ASGI framework/toolkit, which is ideal for building high performance asyncio services.                       |
| [fastapi-users](https://github.com/fastapi-users/fastapi-users) | a customizable users management for FastAPI                                                                                |
| [pydantic](https://github.com/pydantic/pydantic)                | Data validation using Python type hints                                                                                    |
| [jinja2](https://github.com/pallets/jinja/)                     | a fast, expressive, extensible templating engine                                                                           |

## Contributing

- Feel free to contribute both to `main` and `develop-1.x` branches. The latter one is for future major release. This project uses [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)