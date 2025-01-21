package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"path"

	"github.com/okhuz/openapi2krakend/pkg/converter"
	"github.com/okhuz/openapi2krakend/pkg/utility"
)

func downloadSwagger(url string) ([]byte, error) {
    resp, err := http.Get(url)
    if err != nil {
        return nil, fmt.Errorf("failed to download swagger: %v", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("failed to download swagger: status code %d", resp.StatusCode)
    }

    return io.ReadAll(resp.Body)
}

func main() {
    inputURL := flag.String("i", "", "URL of the swagger/OpenAPI JSON specification")
    outputPath := flag.String("o", "output/krakend.json", "Output path for KrakenD configuration")
    
    flag.Parse()

    if *inputURL == "" {
        fmt.Println("Error: Input URL is required")
        flag.PrintDefaults()
        os.Exit(1)
    }

    // Download swagger specification
    swaggerData, err := downloadSwagger(*inputURL)
    if err != nil {
        fmt.Printf("Error downloading swagger: %v\n", err)
        os.Exit(1)
    }

    // Create temporary file to store the downloaded swagger
    tempDir, err := os.MkdirTemp("", "swagger-*")
    if err != nil {
        fmt.Printf("Error creating temp directory: %v\n", err)
        os.Exit(1)
    }
    defer os.RemoveAll(tempDir)

    tempFile := path.Join(tempDir, "swagger.json")
    if err := os.WriteFile(tempFile, swaggerData, 0644); err != nil {
        fmt.Printf("Error writing temp file: %v\n", err)
        os.Exit(1)
    }

    // Get configuration from environment
    encoding := utility.GetEnv("ENCODING", "json")
    globalTimeout := utility.GetEnv("GLOBAL_TIMEOUT", "3000ms")

    // Convert swagger to KrakenD configuration
    configuration := converter.Convert(tempDir, encoding, globalTimeout)

    // Create output directory if it doesn't exist
    outputDir := path.Dir(*outputPath)
    if err := os.MkdirAll(outputDir, 0777); err != nil {
        fmt.Printf("Error creating output directory: %v\n", err)
        os.Exit(1)
    }

    // Write KrakenD configuration
    file, err := json.MarshalIndent(configuration, "", " ")
    if err != nil {
        fmt.Printf("Error marshaling configuration: %v\n", err)
        os.Exit(1)
    }

    if err := os.WriteFile(*outputPath, file, 0644); err != nil {
        fmt.Printf("Error writing output file: %v\n", err)
        os.Exit(1)
    }

    fmt.Printf("Successfully generated KrakenD configuration at %s\n", *outputPath)
}