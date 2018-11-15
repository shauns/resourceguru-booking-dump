# ResourceGuru booking dump

This script dumps all the bookings from ResourceGuru into a PostgreSQL table (JSONB).

## Environment variables

You can use a `.env` file.

- `CLIENT_ID`, `CLIENT_SECRET`, `DOMAIN` as per ResourceGuru app
- `USERNAME`, `PASSWORD` credentials for login to ResourceGuru
- `DB_CONNECTION` where to store the data, psyscopg2 connection string

## Useful queries

Get the minutes logged of the people who've completed RG for the current week:

```sql
select name, sum(duration::numeric) from detailed_bookings where start_time >= date_trunc('week', now()) and end_time < date_trunc('week', now() + interval '1 week') group by name order by sum(duration::numeric) desc;
```
