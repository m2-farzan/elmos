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
docker exec -i ${PROJECT_BASENAME}-db mysql -u$DB_USER -p$DB_PASS $DB_DATABASE < data.sql
```

Save database to dump:

```bash
docker exec -i ${PROJECT_BASENAME}-db mysqldump -u$DB_USER -p$DB_PASS $DB_DATABASE > ${PROJECT_BASENAME}-db_$(date +%Y-%b-%d_%H-%M_%z).sql
```

See latest logins:

```bash
docker exec -i ${PROJECT_BASENAME}-db mysql -u$DB_USER -p$DB_PASS $DB_DATABASE -e "SELECT last_access, id, department_id, gender, email FROM users ORDER BY last_access DESC LIMIT 16"
```

# Hot Deployment
Elmos-Vahed uses blue/green deployment pattern for zero-downtime deployment. The steps to achieve an update are demonstrated below:

```bash
# Pull the latest changes
git pull origin master

# Setup environment
export $(xargs <.env)

# Build and run *green* instance of the web app
docker-compose -f docker-compose-green.yml up --build -d

# Now the green instance can be tested on $UI_PORT_GREEN.
# The green instance is still not visible to end users.

# Now let's update reverse proxy config.
sed -i "s/$UI_PORT/$UI_PORT_GREEN/g" /etc/nginx/sites-available/ir.elmos-vahed

# Validate new config
nginx -t

# Gracefully reload
nginx -s reload

# Now the green instance is visible.
# Since blue is still running, you can quickly roll back if you need.

# If everything is good, the blue instance can safely get updated (no suffix for blue)
docker-compose up -d --no-deps --build elmos

# Roll back to blue, leaving green free for the next update
sed -i "s/$UI_PORT_GREEN/$UI_PORT/g" /etc/nginx/sites-available/ir.elmos-vahed
nginx -t
nginx -s reload

# If you really want to free the ~60 MB's memory used by green, you can do it:
docker-compose -f docker-compose-green.yml stop
```
