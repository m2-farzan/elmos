# Steps to configure database for the first time

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

Start docker-compose.

Populate departments:

```bash
$ELMOS/utils/dbconfig/initialize-db-dockerized.sh
```

Populate units:

```bash
curl -X POST -F "data_avail=@data_avail.xml" -F "data_na=@data_na.xml" http://127.0.0.1:${DBWRITER_PORT}/
```

That's it. This is not a frequent thing so I didn't bother automating it.
