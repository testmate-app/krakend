package converter

import (
	"fmt"
	"io/fs"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
	"testing"
)

// Load the OpenAPI JSON from a URL
func loadFromURL(url string) ([]byte, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("failed to fetch from URL: %s, status code: %d", url, resp.StatusCode)
	}

	return ioutil.ReadAll(resp.Body)
}

// Test loading from a URL
func TestLoadFromURL(t *testing.T) {
	url := os.Getenv("TEST_URL")
	if url == "" {
		t.Fatal("TEST_URL environment variable not set")
	}

	openApiDefinition, err := loadFromURL(url)

	if err != nil {
		t.Errorf("Failed to load from URL: %v", err)
	}

	if openApiDefinition == nil {
		t.Error("Got nil servers; expected openApiDefinition")
	}
}

// Test loading from a file
func TestLoadFromFile(t *testing.T) {
	path := getSwaggerFolder()
	openApiDefinition := loadFromFile(fmt.Sprintf("%s/pet-store.json", path)) // Calls the existing loadFromFile in utility.go

	if openApiDefinition == nil {
		t.Error("Got nil servers; expected openApiDefinition")
	}c
}

// Test function for filtering files
func TestFilterFiles(t *testing.T) {
	var swaggerFiles []fs.FileInfo
	if files, err := ioutil.ReadDir(getSwaggerFolder()); err == nil {
		swaggerFiles = filterFiles(files)
	}
	numberOfFiles := len(swaggerFiles)
	if numberOfFiles != 1 {
		t.Errorf("Got %d #files; expected 1", numberOfFiles)
	}
}

// Helper to get the Swagger folder path
func getSwaggerFolder() string {
	path, err := os.Getwd()
	if err != nil {
		log.Println(err)
	}
	path = strings.ReplaceAll(path, "/pkg/converter", "")
	return fmt.Sprintf("%s/swagger", path)
}
