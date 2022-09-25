# wildfire_analysis

Analysis of US wildfires data from 1992-2015 based on [kaggle dataset](https://www.kaggle.com/datasets/rtatman/188-million-us-wildfires)

## Objectives

This repo tries to answer below questions

Q1: Have wildfires become more or less frequent over time?
Q2: What counties are the most and least fire-prone?
Q3: Given the size, location and date, can you predict the cause of a wildfire?


To answer these questions repo is divided into 2 parts.

1. Web app based on Streamlit.
   This app helps to answer first 2 questions of the problem statement with some additional information.
2. Jupyter notebook
   This notebook explores classification problem defined in the Q3 above. 

## Usage

This simple web application is based on below guiding principles.

- Modularity,
- Reusability and
- Replicability
  
## Requirements

### Compile and runtime Requirements

1. [Docker](https://www.docker.com/)
2. [Docker compose](https://docs.docker.com/compose/)
3. Web browser, tested on Chrome

### Development technologies

1. [Python](https://www.python.org/)
2. [Streamlit](https://streamlit.io/)
3. [PostgreSql](https://www.postgresql.org/)

## How to run Web app

---

App can be executed using one of the 2 methods listed below.

For DB configuration it uses `.env` file in `docker-compose.yml`.
 
### 1. Docker compose

There is a pre-built docker image for the app service available on [arundeep78/wildfires:latest](https://hub.docker.com/r/arundeep78/wildfires) based on Dockerfile.

If you make changes to the app or anything else in Docker file, you can change `docker-compose.yml` `services.app` section to use `build` section.

1. Clone github repo to local folder
2. Execute below steps 
   1. `docker compose up -d`
3. Open https://localhost in local browser

### 2. VS Code

If you use VS code for development, then you can execute and change the application as needed. This setup is based on [VS Code Remote development](https://code.visualstudio.com/docs/remote/remote-overview) especially Remote Containers and [dev containers](https://code.visualstudio.com/docs/remote/containers-tutorial).

1. Clone github repo to local folder
2. Open the folder in VS Code.
3. Open VS Command `Remote Containers: Reopen in container`.
4. Initial build will download the data file and initiate postgresql DB.
5. Above command should be able to download data file in the container while building the container. it needs kaggle api details, which is provided in `.devcontainer/.env`. You can change them to your personal account.
6. Launch the application with `F5` or `Ctrl+F5`. There is a default `.vscode/launch.json`

## Jupyter notebook for classification

Jupyter notebook depends on certain python libraries. All Requirements libraries/packages are listed in `requirements.txt` file.

### If using VS Code development containers

Repo contains [VS code development configuration](https://code.visualstudio.com/docs/remote/containers-tutorial), which allows to open the repo in a container to execute Jupyter notebook in an environment with all dependencies already setup.

At the time of container build [dataset file from kaggle](https://www.kaggle.com/datasets/rtatman/188-million-us-wildfires) will be downloaded and stored  in `app/db/wildfires_us.sqlite`. This file is not uploaded to repo due to size limits.

### If you are using different python environment

1. Please install all required packages using requirements.txt file.
2. Configure `'SQLITE_DB_FILE` in your os environment to locations of the sqlite file. SQLlite file can be downloaded from [kaggle datasets](https://www.kaggle.com/datasets/rtatman/188-million-us-wildfires). Default path is configured in `wf_classifier.ipynb`. Alternatively, you can also set the path directly in the notebook file.