dev:
	docker-compose -f backend/docker-compose.yml down
	docker-compose -f backend/docker-compose.yml build
	docker-compose -f backend/docker-compose.yml up

exec: 
	docker-compose -f backend/docker-compose.yml exec stac_server /bin/bash