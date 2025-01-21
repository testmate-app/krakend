import os
import json
import time
import logging.config
import redis
from flask import Flask, request, jsonify
import requests
from prometheus_client import start_http_server, Counter, Gauge
from json_logger import JsonLogger
from datetime import datetime
import yaml

# Configure logging
with open('logging_config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    logging.config.dictConfig(config)

logger = JsonLogger('krakend_updater')

app = Flask(__name__)

# Redis configuration
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

# Prometheus metrics
config_updates = Counter('krakend_config_updates_total', 'Total number of config updates')
deployment_duration = Gauge('krakend_deployment_duration_seconds', 'Time taken for deployment')
service_health = Gauge('krakend_service_health', 'Health status of KrakenD service')
config_validation_errors = Counter('krakend_config_validation_errors', 'Number of configuration validation errors')

class KrakenDConfig:
    def __init__(self, config_path):
        self.config_path = config_path
        self.current_version = self._get_latest_version()

    def _get_latest_version(self):
        try:
            return redis_client.get('krakend_current_version')
        except:
            return None

    def _save_version(self, version):
        redis_client.set('krakend_current_version', version)
        redis_client.set(f'krakend_config_{version}_timestamp', datetime.now().isoformat())

    def generate_config(self, swagger_spec):
        """Generate KrakenD configuration from Swagger spec"""
        version = time.strftime("%Y%m%d_%H%M%S")
        
        endpoints = []
        for path, methods in swagger_spec['paths'].items():
            for method, details in methods.items():
                if method.lower() in ['get', 'post', 'put', 'delete']:
                    endpoint = {
                        "endpoint": path,
                        "method": method.upper(),
                        "backend": [{
                            "url_pattern": path,
                            "host": ["http://backend-service:8080"],
                            "method": method.upper(),
                            "encoding": "json",
                            "extra_config": {
                                "backend/http": {
                                    "return_error_details": "backend_error"
                                }
                            }
                        }]
                    }
                    endpoints.append(endpoint)

        config = {
            "version": 3,
            "name": f"krakend-config-{version}",
            "cache_ttl": "3600s",
            "timeout": "3s",
            "endpoints": endpoints,
            "extra_config": {
                "security/cors": {
                    "allow_origins": ["*"],
                    "allow_methods": ["GET", "POST", "PUT", "DELETE"],
                    "allow_headers": ["Origin", "Authorization", "Content-Type"],
                    "expose_headers": ["Content-Length"],
                    "max_age": "12h"
                },
                "telemetry/metrics": {
                    "collection_time": "60s",
                    "listen_address": ":8090",
                    "router_disabled": false,
                    "proxy_disabled": false,
                    "backend_disabled": false,
                },
                "telemetry/logging": {
                    "level": "DEBUG",
                    "prefix": "[KRAKEND]",
                    "syslog": false,
                    "stdout": true
                },
                "security/ratelimit/router": {
                    "max_rate": 50,
                    "client_max_rate": 5,
                    "strategy": "ip"
                }
            }
        }

        config_path = os.path.join(self.config_path, f"krakend_{version}.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        self._save_version(version)
        logger.info(f"Generated new config version: {version}")
        return version, config_path

    def validate_config(self, config_path):
        """Validate KrakenD configuration"""
        try:
            # Syntax check
            result = os.system(f"krakend check -t -d {config_path}")
            if result != 0:
                raise Exception("Config syntax validation failed")

            # Lint check
            result = os.system(f"krakend check -c {config_path} --lint")
            if result != 0:
                raise Exception("Config lint check failed")

            logger.info("Config validation passed")
            return True
        except Exception as e:
            logger.error(f"Config validation failed: {str(e)}")
            config_validation_errors.inc()
            return False

class PortainerClient:
    def __init__(self, url, username, password, endpoint):
        self.url = url
        self.username = username
        self.password = password
        self.endpoint = endpoint
        self.token = None
        self._authenticate()

    def _authenticate(self):
        try:
            response = requests.post(
                f"{self.url}/api/auth",
                json={
                    "username": self.username,
                    "password": self.password
                }
            )
            response.raise_for_status()
            self.token = response.json()['jwt']
        except Exception as e:
            logger.error(f"Portainer authentication failed: {str(e)}")
            raise

    def _get_headers(self):
        if not self.token:
            self._authenticate()
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def update_service(self, service_id, config_path):
        """Update KrakenD service with new configuration"""
        try:
            with open(config_path, 'r') as f:
                config_data = f.read()

            service = self.get_service(service_id)
            if not service:
                raise Exception(f"Service {service_id} not found")

            new_config = {
                "Name": service['Spec']['Name'],
                "TaskTemplate": {
                    "ContainerSpec": {
                        "Image": service['Spec']['TaskTemplate']['ContainerSpec']['Image'],
                        "Configs": [{
                            "File": {
                                "Name": "/etc/krakend/krakend.json",
                                "UID": "0",
                                "GID": "0",
                                "Mode": 292
                            },
                            "ConfigID": config_data
                        }]
                    }
                },
                "Mode": service['Spec']['Mode']
            }

            response = requests.post(
                f"{self.url}/api/endpoints/{self.endpoint}/docker/services/{service_id}/update",
                headers=self._get_headers(),
                json=new_config
            )
            response.raise_for_status()
            logger.info(f"Service {service_id} updated successfully")
            return True

        except Exception as e:
            logger.error(f"Service update failed: {str(e)}")
            return False

    def get_service(self, service_id):
        """Get service details from Portainer"""
        try:
            response = requests.get(
                f"{self.url}/api/endpoints/{self.endpoint}/docker/services/{service_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get service details: {str(e)}")
            return None

class KrakenDManager:
    def __init__(self):
        self.config = KrakenDConfig(os.getenv('KRAKEND_CONFIG_PATH', '/krakend-config'))
        self.portainer = PortainerClient(
            os.getenv('PORTAINER_URL'),
            os.getenv('PORTAINER_USERNAME'),
            os.getenv('PORTAINER_PASSWORD'),
            os.getenv('PORTAINER_ENDPOINT')
        )

    def update_krakend(self, swagger_url):
        """Main update process for KrakenD"""
        try:
            # Download swagger spec
            response = requests.get(swagger_url)
            response.raise_for_status()
            swagger_spec = response.json()

            # Generate new config
            version, config_path = self.config.generate_config(swagger_spec)

            # Validate config
            if not self.config.validate_config(config_path):
                raise Exception("Configuration validation failed")

            # Update service
            if not self.portainer.update_service('krakend-service', config_path):
                raise Exception("Service update failed")

            # Update metrics
            config_updates.inc()
            return version

        except Exception as e:
            logger.error(f"KrakenD update failed: {str(e)}")
            raise

krakend_manager = KrakenDManager()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        redis_client.ping()
        return jsonify({'status': 'healthy'}), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({'status': 'unhealthy'}), 500

@app.route('/update', methods=['POST'])
def handle_update():
    """Handle update requests"""
    try:
        data = request.json
        start_time = time.time()

        if data['event'] != 'backend_updated':
            raise Exception("Invalid event type")

        version = krakend_manager.update_krakend(data['swagger_url'])
        deployment_duration.set(time.time() - start_time)
        service_health.set(1)

        return jsonify({
            'status': 'success',
            'message': 'KrakenD updated successfully',
            'version': version
        })

    except Exception as e:
        logger.error(f"Update request failed: {str(e)}")
        service_health.set(0)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Start Prometheus metrics server
    start_http_server(8000)
    # Start update service
    app.run(host='0.0.0.0', port=5000)