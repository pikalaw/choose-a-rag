hostname = okapi.c.googlers.com

start:
	uvicorn api.server:app --reload --host ${hostname} --port 8000

check_type:
	mypy

unittest:
	python3 -m unittest discover

test: check_type unittest;

kill-server:
	fuser -k 8000/tcp
