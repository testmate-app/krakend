import argparse
import json
import yaml
import os
import requests
from typing import Dict, List
from urllib.parse import urlparse

class OpenAPIToKrakenD:
    def __init__(self, openapi_source: str, output_file: str, bearer_token: str = None):
        self.openapi_source = openapi_source
        self.output_file = output_file
        self.bearer_token = bearer_token
        self.spec = self._load_spec()
        
    def _load_spec(self) -> Dict:
        """Load OpenAPI specification from URL or file"""
        if self.openapi_source.startswith(('http://', 'https://')):
            headers = {}
            if self.bearer_token:
                headers['Authorization'] = f'Bearer {self.bearer_token}'
            
            response = requests.get(self.openapi_source, headers=headers)
            response.raise_for_status()
            
            if self.openapi_source.endswith(('.yaml', '.yml')):
                return yaml.safe_load(response.text)
            return response.json()
        else:
            with open(self.openapi_source, 'r') as f:
                if self.openapi_source.endswith(('.yaml', '.yml')):
                    return yaml.safe_load(f)
                return json.load(f)
    
    def _extract_base_url(self) -> str:
        """Extract base URL from servers section"""
        if 'servers' in self.spec and self.spec['servers']:
            url = self.spec['servers'][0]['url']
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}"
        return "http://localhost:8080"

    def _convert_path_to_endpoint(self, path: str, methods: Dict) -> List[Dict]:
        """Convert OpenAPI path to KrakenD endpoint configuration"""
        endpoints = []
        
        for method, details in methods.items():
            if method.upper() not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                continue
                
            endpoint = {
                "endpoint": path,
                "method": method.upper(),
                "backend": [{
                    "url_pattern": path,
                    "method": method.upper(),
                    "host": [self._extract_base_url()],
                    "extra_config": {}
                }]
            }
            
            # Handle query parameters
            if 'parameters' in details:
                query_params = [
                    param['name'] for param in details['parameters']
                    if param['in'] == 'query'
                ]
                if query_params:
                    endpoint['input_query_strings'] = sorted(query_params)
            
            # Add output encoding
            if 'responses' in details:
                endpoint['output_encoding'] = 'json'
                
            endpoints.append(endpoint)
            
        return endpoints

    def generate_endpoints(self) -> List[Dict]:
        """Generate only the endpoints array for KrakenD configuration"""
        endpoints = []
        
        for path, methods in self.spec['paths'].items():
            endpoints.extend(self._convert_path_to_endpoint(path, methods))
            
        # Sort endpoints by path and then by method
        endpoints.sort(key=lambda x: (x['endpoint'], x['method']))
            
        return endpoints

    def save_endpoints(self):
        """Save the generated endpoints configuration"""
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            
        # Generate and save endpoints
        endpoints = {
            "endpoints": self.generate_endpoints()
        }
        
        # Save endpoints configuration
        with open(self.output_file, 'w') as f:
            json.dump(endpoints, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Convert OpenAPI spec to KrakenD endpoints')
    parser.add_argument('-f', '--file', required=True, help='Path or URL to OpenAPI specification')
    parser.add_argument('-o', '--output', required=True, help='Output file path for KrakenD endpoints')
    parser.add_argument('-t', '--token', help='Bearer token for API authentication')
    
    args = parser.parse_args()
    
    converter = OpenAPIToKrakenD(args.file, args.output, args.token)
    converter.save_endpoints()
    
if __name__ == '__main__':
    main()