docker/build:
	docker-compose build

docker/up-build:
	docker-compose up --build

run:
	docker-compose up -d

test/local:
	docker-compose exec inoa-challenge pytest -x --ds=inoa_challenge.test_settings --failed-first $(ARGS)

create-env:
	cp .env.example .env
