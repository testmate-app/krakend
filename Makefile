.PHONY: start stop restart logs compile-flexible-config elastic

start:
	docker-compose up -d

stop:
	docker-compose down --volumes

restart:
	docker-compose restart

logs:
	docker-compose logs -f logstash

compile-flexible-config:
	docker run \
        -v "./config/:/etc/krakend/" \
        -e "FC_DEBUG=true" \
        -e "FC_CONFIG=/etc/krakend/fc_config.json" \
        krakend/krakend-ee \
        check -c krakend.tmpl

# elastic:
# 	curl -X POST "localhost:5601/api/saved_objects/_import" -H "kbn-xsrf: true" --form file=@config/elastic/dashboard.ndjson -H "kbn-xsrf: true"