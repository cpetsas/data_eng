# N&L Assessment

## System dependencies
Developed in Ubuntu 20.04 with WSL1
- Python3 and pip
- Redis Server

## Project Dependencies
- Create a venv by running:
```sh
    python3 -m venv NLvenv
```
- Install all dependencies in the Nlvenv by activating it:
```sh
    source /path/to/NLvenv/bin/activate
```
and then run:
```sh
    pip install -r /patt/to/requirements.txt
```

## Deploying the system
Unfortunately I didn't have enough time to work on deploying the system with docker so there are some manual steps we need to take to deploy it.
Create a directory called 'reports' in the root of the system
- Start a redis server:
```sh
    sudo redist-server
```
- Run bash script make_workers.sh
```sh
    bash make_workers.sh
```
This creates 3 instances of the py file worker.py that listen to enqueued jobs in the redis Q.
- Run
```sh
    python3 pipeline_manager.py
```
This, simulates traffic in the queue by pushing some content in the Redis Q every few seconds.
- Finally, run
```sh
    python3 watcher.py
```
This is an infinite loop which listens for content in the Redis Q and creates a job which the workers execute.
