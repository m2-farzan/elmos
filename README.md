# Install

Run web app:

```bash
docker build -t elmos:latest .
docker-compose up
```

Load database from dump:

```bash
docker exec -i elmos-db mysql -uelmos_vahed -pCHANGE_ME elmos_units < data.sql
```
