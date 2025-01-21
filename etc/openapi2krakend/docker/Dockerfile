FROM alpine:latest

RUN mkdir /openapi2krakend && \
    mkdir /openapi2krakend/swagger && \
    mkdir /openapi2krakend/output

ENV ENABLE_LOGGING=true
ENV LOG_LEVEL=DEBUG
ENV LOG_PREFIX="[TEST]"
ENV ALLOWED_ORIGINS="*"
ENV ENABLE_CORS="true"
ENV GLOBAL_TIMEOUT="3600s"
ENV ENCODING="no-op"
ENV LOGGER_SKIP_PATHS="/__health"
ENV PATH_PREFIX="v1"
ENV DEBUG=true
ENV ADDITIONAL_PATHS="/management/prometheus"

COPY ../docker/init-script.sh /openapi2krakend/init-script.sh
COPY ../build/openapi2krakend /openapi2krakend/openapi2krakend
RUN chmod +x /openapi2krakend/init-script.sh && \
    chmod +x /openapi2krakend/openapi2krakend
