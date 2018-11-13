# ResourceGuru booking dump

This script dumps all the bookings from ResourceGuru into a PostgreSQL table (JSONB).

## Environment variables

You can use a `.env` file.

- `CLIENT_ID`, `CLIENT_SECRET`, `DOMAIN` as per ResourceGuru app
- `USERNAME`, `PASSWORD` credentials for login to ResourceGuru
- `DB_CONNECTION` where to store the data, psyscopg2 connection string
