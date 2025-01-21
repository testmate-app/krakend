# API Gateway USU - Krakend dengan Integrasi RabbitMQ

## Deskripsi

Repository ini berisi contoh implementasi API Gateway untuk Universitas Sumatera Utara (USU) menggunakan [Krakend](https://www.krakend.io/) yang terintegrasi dengan [RabbitMQ](https://www.rabbitmq.com/). API Gateway ini menyediakan dua endpoint utama:

- **Produce**: Mengirim pesan ke RabbitMQ.
- **Consume**: Mengambil pesan dari RabbitMQ.

API Gateway ini dapat digunakan untuk memfasilitasi komunikasi antar layanan melalui pesan berbasis queue menggunakan RabbitMQ sebagai broker pesan.

## Fitur

- **Integrasi RabbitMQ**: Mendukung pengiriman dan pengambilan pesan dari RabbitMQ melalui endpoint Krakend.

## Arsitektur

## Persyaratan

- [Docker](https://www.docker.com/) dan [Docker Compose](https://docs.docker.com/compose/)
- Krakend CE
- RabbitMQ

## Cara Menjalankan

1. **Jalankan** RabbitMQ dan Krakend dengan Docker Compose:

   ```bash
   docker-compose up
   ```

2. Akses **API Gateway** di `http://localhost:8080`.

3. Bisa jalankan `consume.sh` atau `produce.sh`
