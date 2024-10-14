default:
	@echo "Please specify a target to build"

clean:
	rm -rf static
	mkdir static
	touch static/.gitkeep

build-ui: clean
	cd ../mymdnotes && bun run build --mode=prod
	cp -r ../mymdnotes/dist/* static/

NAME=am8850/zebra
TAG=0.0.4a
docker-build: build-ui
	docker build -t $(NAME):$(TAG) .

docker-push:
	docker push $(NAME):$(TAG)

	