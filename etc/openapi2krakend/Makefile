.PHONY: build dockerize test run

build:
	rm -rf ./build && \
	env GOOS=linux GOARCH=amd64 ENABLE_LOGGING=true LOG_LEVEL=DEBUG LOG_PREFIX="[TEST]" ALLOWED_ORIGINS="*" ENABLE_CORS="true" GLOBAL_TIMEOUT="3600s" ENCODING="no-op" LOGGER_SKIP_PATHS="/__health" PATH_PREFIX="v1" DEBUG=true ADDITIONAL_PATHS="/management/prometheus" go build -o ./build/openapi2krakend ./pkg
	upx -9 ./build/openapi2krakend

dockerize: build
	docker buildx build --platform=linux/amd64 -f docker/Dockerfile --build-arg ENABLE_LOGGING=true --build-arg LOG_LEVEL=DEBUG --build-arg LOG_PREFIX="[TEST]" --build-arg ALLOWED_ORIGINS="*" --build-arg ENABLE_CORS="true" --build-arg GLOBAL_TIMEOUT="3600s" --build-arg ENCODING="no-op" --build-arg LOGGER_SKIP_PATHS="/__health" --build-arg PATH_PREFIX="v1" --build-arg DEBUG=true --build-arg ADDITIONAL_PATHS="/management/prometheus" -t okhuz/openapi2krakend:0.1.6 .

test:
	go test ./... -v

run:
	./scripts/run.sh