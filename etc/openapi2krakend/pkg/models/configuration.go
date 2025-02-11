package models

import (
	"strings"

	"github.com/okhuz/openapi2krakend/pkg/utility"
)

type Backend struct {
	UrlPattern          string   `json:"url_pattern"`
	Encoding            string   `json:"encoding"`
	Method              string   `json:"method"`
	Host                []string `json:"host"`
	DisableHostSanitize bool     `json:"disable_host_sanitize"`
}

func NewBackend(host string, endpoint string, method string, outputEncoding string) Backend {
	return Backend{
		UrlPattern:          endpoint,
		Encoding:            outputEncoding,
		Method:              strings.ToUpper(method),
		Host:                []string{host},
		DisableHostSanitize: false,
	}
}

type Endpoint struct {
	Endpoint          string    `json:"endpoint"`
	Method            string    `json:"method"`
	OutputEncoding    string    `json:"output_encoding"`
	Timeout           string    `json:"timeout"`
	InputQueryStrings []string  `json:"input_query_strings"`
	Backend           []Backend `json:"backend"`
	InputHeaders      []string  `json:"input_headers"`
}

func NewEndpoint(host string, endpoint string, backendEndpoint string, method string, outputEncoding string, timeout string) Endpoint {
	backend := NewBackend(host, backendEndpoint, method, outputEncoding)
	return Endpoint{
		Endpoint:          endpoint,
		Method:            strings.ToUpper(method),
		OutputEncoding:    outputEncoding,
		Timeout:           timeout,
		InputQueryStrings: []string{},
		Backend:           []Backend{backend},
		InputHeaders:      []string{"Content-Type"},
	}
}

func (e *Endpoint) InsertQuerystringParams(param string) {
	e.InputQueryStrings = append(e.InputQueryStrings, param)
}

func (e *Endpoint) InsertHeadersToPass(header string) {
	e.InputHeaders = append(e.InputHeaders, header)
}

type Configuration struct {
	Schema         string                 `json:"$schema"`
	Version        string                 `json:"version"`
	Timeout        string                 `json:"timeout"`
	CacheTtl       string                 `json:"cache_ttl"`
	OutputEncoding string                 `json:"output_encoding"`
	Name           string                 `json:"name"`
	Endpoints      []Endpoint             `json:"endpoints"`
	ExtraConfig    map[string]interface{} `json:"extra_config,omitempty"`
}

func NewConfiguration(outputEncoding string, timeout string) Configuration {
	var extraConfig = make(map[string]interface{}, 15)

	if utility.GetEnv("ENABLE_CORS", "false") == "true" {
		extraConfig["security/cors"] = NewCors()
	}
	if utility.GetEnv("ENABLE_LOGGING", "false") == "true" {
		extraConfig["telemetry/logging"] = NewLogging()
	}

	var loggerSkipPaths = utility.GetEnv("LOGGER_SKIP_PATHS", "")

	if loggerSkipPaths != "" {
		extraConfig["router"] = Router{
			LoggerSkipPaths: strings.Split(loggerSkipPaths, ","),
		}
	}

	return Configuration{
		Schema:         "https://www.krakend.io/schema/v3.json",
		Version:        "3",
		Timeout:        timeout,
		CacheTtl:       "300s",
		OutputEncoding: outputEncoding,
		Name:           "Tenera API",
		Endpoints:      []Endpoint{},
		ExtraConfig:    extraConfig,
	}
}

func (c *Configuration) InsertEndpoint(endpoint Endpoint) {
	c.Endpoints = append(c.Endpoints, endpoint)
}

// Modified to accept original Endpoint type
type SimpleBackend struct {
    BackendUrlPattern string `json:"backend_url_pattern"`
    BackendMethod     string `json:"backend_method"`
    BackendHost       string `json:"backend_host"`
}

type SimpleEndpoint struct {
    Endpoint string `json:"endpoint"`
    Method   string `json:"method"`
    SimpleBackend
}

type SimpleConfiguration struct {
    Endpoints []SimpleEndpoint `json:"endpoints"`
}

// Convert regular Endpoint to SimpleEndpoint
func ConvertToSimpleEndpoint(e Endpoint) SimpleEndpoint {
    // Assuming we take the first backend if multiple exist
    var backendHost, backendPattern, backendMethod string
    if len(e.Backend) > 0 {
        backendHost = e.Backend[0].Host[0]
        backendPattern = e.Backend[0].UrlPattern
        backendMethod = e.Backend[0].Method
    }

    return SimpleEndpoint{
        Endpoint: e.Endpoint,
        Method:   e.Method,
        SimpleBackend: SimpleBackend{
            BackendUrlPattern: backendPattern,
            BackendMethod:     backendMethod,
            BackendHost:       backendHost,
        },
    }
}

func NewSimpleConfiguration(outputEncoding string, timeout string) SimpleConfiguration {
    var extraConfig = make(map[string]interface{}, 15)

    if utility.GetEnv("ENABLE_CORS", "false") == "true" {
        extraConfig["security/cors"] = NewCors()
    }
    if utility.GetEnv("ENABLE_LOGGING", "false") == "true" {
        extraConfig["telemetry/logging"] = NewLogging()
    }

    var loggerSkipPaths = utility.GetEnv("LOGGER_SKIP_PATHS", "")

    if loggerSkipPaths != "" {
        extraConfig["router"] = Router{
            LoggerSkipPaths: strings.Split(loggerSkipPaths, ","),
        }
    }

    return SimpleConfiguration{
        Endpoints: []SimpleEndpoint{},
    }
}

// Modified to accept original Endpoint type
func (c *SimpleConfiguration) InsertEndpoint(endpoint Endpoint) {
    simpleEndpoint := ConvertToSimpleEndpoint(endpoint)
    c.Endpoints = append(c.Endpoints, simpleEndpoint)
}
