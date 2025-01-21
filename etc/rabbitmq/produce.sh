curl --location 'http://localhost:8080/produce/foo' \
--header 'Content-Type: application/json' \
--data '{
    "status": "success",
    "error": false,
    "message": "create billing successfully",
    "data": {
        "id": "66bddfc9fee6164812dbc1a1",
        "bank_id": "623bfac829cc803d85cab842",
        "bank_code": "BNI"
    }
}'