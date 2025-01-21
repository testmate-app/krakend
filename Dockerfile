FROM devopsfaith/krakend AS builder
ARG ENV=dev

COPY ./krakend /etc/krakend

## Save temporary file to /tmp to avoid permission errors
RUN FC_ENABLE=1 \
    FC_SETTINGS="/etc/krakend/config/settings" \
    FC_PARTIALS="/etc/krakend/config/partials" \
    FC_TEMPLATES="/etc/krakend/config/templates" \
    FC_OUT="/etc/krakend/krakend.json" \
    krakend check -d -t -c krakend.tmpl

# The linting needs the final krakend.json file
RUN krakend check -c krakend.json --lint

FROM devopsfaith/krakend
COPY --from=builder --chown=krakend /etc/krakend/krakend.json .


EXPOSE 8080

# Uncomment with Enterprise image:
# COPY LICENSE /etc/krakend/LICENSE
