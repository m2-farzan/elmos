# Database Writer V2

This microservice receives the XML tables that are read from golestan
reports. This data transfer is done via HTTP.

Then, it parses the table and updates the application database based
on the information. It also saves some metadata on disk including
last update time, errors log, etc.