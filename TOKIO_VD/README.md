# Automigi base

## Features

- Basic component-oriented architecture template.
- Dockerfile setup.
- Parameter converter configuration files.

# Tabla de contenido
- [Definition](#Definition)
- [Objective](#Objective)
- [Structure](#Structure)
- [Functions](#Functions)
- [Environment setup](#environmentsetup)


## Definition:
Basic python bash setup

## Objective:
This project was made with the purpose of making easier a quick development of a python bash based application.

## Structure:
Project folder structure 

    │   .dockerignore
    │   .gitignore
    │   Dockerfile
    │   README.md
    │   requirements.txt
    └───app # Folder to store all application business logic
        │   environment.py # Read environment variables
        │   main.py # Main process
        │   __init__.py # Tell python that app folder is a module
        └───params # Contains logic to read arguments passed on execution time
                parameters.py # Main args converter
                __init__.py

## Functions:

### Function: main

Prints a hello world message with values of MESSAGE environment variables and name argument

1. Parameters: None
2. Returns: None

```
This is a Hello World project.
La variable de ambiente MESSAGE es: Hola
El valor del argumento --name es: Andres
```

## Environment setup

  Install [``Miniconda``](https://docs.conda.io/en/latest/miniconda.html) on your local machine.

* Create an environment with conda to execute the application

  ```BASH
  conda create --name python-bash-env python=3.8
  ```

* Activate conda environment

  ```BASH
  conda activate python-bash-env
  ```

* A ``.env`` file can be provided in order to load environment variables. The environment variables used in this template are listed below.

  * **NAME** can be set as an example

* Install dependencies
  ```BASH
  python -m pip install -r requirements.txt
  ```

* Run application
  ```BASH
  python app/main.py
  ```