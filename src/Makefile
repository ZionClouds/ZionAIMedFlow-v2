default:
	@echo "Please specify a target to build"


# Build and run the application
NAME=am8850/dips
TAG=0.0.4a
docker-build:
	docker build -t $(NAME):$(TAG) .

# Docker cannot handle double quotes in the .env file
docker-run:
	docker run -p 8000:8000 --env-file=.env.docker $(NAME):$(TAG)

docker-push:
	docker push $(NAME):$(TAG)