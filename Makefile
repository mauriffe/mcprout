.PHONY: run build

build:
	docker-compose up --build

update-master:
	git checkout master
	git pull origin master
	make build

update-dev:
	git checkout develop
	git pull origin develop
	make build