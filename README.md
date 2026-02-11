# barribar-mini-rag
This is a minimal implementation of the RAG model question
answering.

## Requirements
- Python 3.8 or later

#### Install Python using MiniConda

1) Download and install MiniConda from [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)

2) Create a new environment using the following command:
    ```bash
    $ conda create -n mini-rag python=3.8
    ```

3) Activate the environments:
    ```bash
    $ conda activate mini-rag
    ```

### (Optional) Setup your command line interface for better readability

```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```

## Installation

### Install the required packages

```bash
$ pip install -r requirements.txt
```
Set your environement variables in the .env file. Like 'OPEN_API_KEY' value.
### Setup the enviroment variables
```bash
$ cp .env.example .env
```

```bash
$ cd docker 
$ cp .env.example .env
```
update 'env' with your credentials

## Run the FastAPI server
```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

### docker commande
sudo docker stop $(sudo docker ps -aq) # stop all docker (list all running docker)
sudo docker rm $(sudo docker ps -aq) # remove all container
sudo docker rmi $(sudo docker images -q) # remove all images
sudo docker volume rm $(sudo docker volume ls -q) # remove all volumes
sudo docker system prune --all # clear all
sudo docker compose up -d # start docker (-d en background)

