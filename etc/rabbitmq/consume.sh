while true; do
  curl -i --location --request GET 'http://localhost:8080/consume'
  sleep 1 # Beri jeda 1 detik antara permintaan, bisa diubah sesuai kebutuhan
done
