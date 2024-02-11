# TaskifyAPI

API using FastAPI and PostgreSQL to create, share or keep track of tasks. API also has a CRUD System Using JWT and Oauth2 to Create a Complete API that can be used with a frontend project

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Docker (& Docker Compose)

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
$ exec uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Contributing

- Feel free to contribute both to `main` and `develop-1.x` branches. The latter one is for future major release. This project uses [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
## License

This project is licensed under the terms of the MIT license.