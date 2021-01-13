# Steps to configure database for the first time

_I like to perform all the steps described below locally, without using docker or anything fancy._

First make sure to have the correct values set up in `.env` file.

Load the values from `.env` file:
```bash
export $(xargs <.env)
```

Set the repo directory as `$ELMOS`:
```bash
export ELMOS=$(pwd)
```

CD into a clean folder:
```bash
cd ../tmp
```

Download a copy of the units data from golestan using golman:
```bash
python $ELMOS/microservices/golman/manual.py
```

Create stub json config files. The script will fill up the file with best guesses.
```bash
python $ELMOS/utils/dbconfig/create-stub-json.py
```

Inspect the generated json files and fix errors if any.

Start mysql if you haven't.
```bash
sudo systemctl start mysqld.service
```

Make sure there is no database with the same name of the database we want to create.
```bash
echo $DB_DATABASE
sudo mysql -e "SHOW DATABASES"
```

So let's create the database. Run these:
```bash
sudo mysql -e "CREATE DATABASE ${DB_DATABASE}"
sudo mysql -e "GRANT ALL PRIVILEGES ON ${DB_DATABASE}.* TO ${DB_USER}@localhost IDENTIFIED BY '${DB_PASS}'"
sudo mysql -e "FLUSH PRIVILEGES" # not sure if needed at all.
```

Now the script can populate departments:
```bash
python $ELMOS/utils/dbconfig/initialize-db.py
```

To fill the units do this: (alternatively skip this and sign in when golman is running as a service):

```bash
env DBWRITER_ENDPOINT=http://127.0.0.1:${DBWRITER_PORT}/ python $ELMOS/microservices/golman/manual.py
# OR
curl -X POST -F "data_avail=@data_avail.xml" -F "data_na=@data_na.xml" http://127.0.0.1:${DBWRITER_PORT}/
```

Now just export the database:

```bash
mysqldump -u$DB_USER -p$DB_PASS $DB_DATABASE > ${DB_DATABASE}-init.sql
```

Move the file into the remote server and load it:
```bash
sudo docker exec -i elmos-db mysql -u$DB_USER -p$DB_PASS $DB_DATABASE < ${DB_DATABASE}-init.sql
```

That's it. This is not a frequent thing so I didn't bother automating it.

---

To initialize a dockerized database, use:

```bash
# python $ELMOS/utils/dbconfig/initialize-db.py
./initialize-db-dockerized.sh
```

