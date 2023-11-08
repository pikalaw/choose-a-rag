start:
	uvicorn api.server:app --reload --port 8001

check_type:
	mypy

unittest:
	python3 -m unittest discover

test: check_type unittest;

install-env: install-env-client install-env-server
	echo 'Install done!'

install-env-client:
	npm i

install-env-server:
	python3 -m pip install -r requirements.txt

save-env:
	python3 -m pip freeze > requirements.txt

update-env: update-env-client update-env-server
	echo 'Update done!'

update-env-client:
	npx ncu --upgrade
	npm i

update-env-server:
	python3 -m pip install -r requirements.txt --upgrade
