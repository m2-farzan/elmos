# Database Writer

This microservice receives the html tables that are read from golestan
reports. This data transfer is done via gRPC on a public port.

Then, it parses the table and updates the application database based
on the information. It also saves some metadata on disk including
last update time, errors log, etc.
