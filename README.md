# Stock APP
This module will get communicate with data base which will be storage needed stocks.

# Install DEV environment

```
> sudo apt install python3.11
> sudo apt install python3.11-venv
> python3.11 -m venv .dev-3.11
> source .dev-3.11/bin/activate
> python -m pip install -r setup/requirements_dev.txt
```

# External services

> docker-compose -f docker-compose.yaml up -d
> docker-compose -f docker-compose.yaml down

# Running API in local

```
> uvicorn src.api:app

or to reload after each change:

> uvicorn src.api:app --reload

```
