### Create an environment and install dependencies
```
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```


### Run fast app server
```
$ uvicorn main:app_fastapi --reload
```