### Description

Basic conversion from OpenAPI specification to Krakend config. This is extendable with custom OpenAPI
attributes and more support for both krakend and openapi configurations.

### Supported custom OpenAPI extensions

Example of custom extensions can be found in the `./swagger/pet-store.json`

x-timeout: At top level or at method level modifies timeout for the whole api or for a single endpoint

### Usage

openapi2krakend can be run before the krakend container to generate krakend.json for krakend to consume.
Services can serve their swagger definitions or even from their documentation pages one can download those swagger
files and convert.

### Arguments

-directory: folder where swagger files live. default is swagger folder in repository.
<br>
-encoding: backend encoding for whole endpoints. default is "json".

### Usage

In make file image creation and build has been declared

To build:

```shell
make build
```

To dockerize

```shell
make dockerize
```

To run with sample environment variables

```shell
make run
```

To execute

```shell
./build/openapi2krakend
```

### License

This code refer to [Hamza Oral](https://github.com/HamzaOralK/openapi2krakend)
