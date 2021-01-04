# Install

1. Enter correct environment values in `.env` file.

2. Build and run everything:

    ```bash
    docker-compose up --build
    ```

# Database Operations

First load environment variables into shell:

```bash
export $(xargs <.env)
```

Load database from dump:

```bash
docker exec -i elmos-db mysql -u$DB_USER -p$DB_PASS $DB_DATABASE < data.sql
```

Save database to dump:

```bash
docker exec -i elmos-db mysqldump -u$DB_USER -p$DB_PASS $DB_DATABASE > elmos-db_$(date +%Y-%b-%d_%H-%M_%z).sql
```

See latest logins:

```bash
docker exec -i elmos-db mysql -u$DB_USER -p$DB_PASS $DB_DATABASE -e "SELECT last_access, id, department_id, gender, email FROM users ORDER BY last_access DESC LIMIT 16"
```
