#!/usr/bin/env python
from dotenv import load_dotenv

load_dotenv()
import os
from urllib.parse import urlencode
import json
import requests
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
import psycopg2
from psycopg2.extras import Json
import progressbar

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = "http://localhost/oauth"
authorize_url = (
    "https://api.resourceguruapp.com/oauth/authorize?client_id=%(client_id)s&redirect_uri=%(redirect_uri)s&response_type=code"
    % locals()
)
api_uri = "https://api.resourceguruapp.com/v1/{}/".format(os.getenv("DOMAIN"))

start_date = "2018-01-01"
end_date = "2020-01-01"

print("Authenticating...")

oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
token = oauth.fetch_token(
    token_url="https://api.resourceguruapp.com/oauth/token",
    username=os.getenv("USERNAME"),
    password=os.getenv("PASSWORD"),
    client_id=client_id,
    client_secret=client_secret,
)

print(token)
print("Loading from ResourceGuru: {}".format(api_uri))
bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
i = 0

all_resources = []
offset = 0
limit = 50
while True:
    resources = oauth.get(
        api_uri + "resources", params={"limit": limit, "offset": offset}
    ).json()
    offset = offset + limit
    all_resources = all_resources + resources
    bar.update(i)
    i += 1
    if not resources:
        break

offset = 0
limit = 50
while True:
    resources = oauth.get(
        api_uri + "resources/archived", params={"limit": limit, "offset": offset}
    ).json()
    offset = offset + limit
    all_resources = all_resources + resources
    bar.update(i)
    i += 1
    if not resources:
        break

all_bookings = []

offset = 0
while True:
    bookings = oauth.get(
        api_uri + "bookings",
        params={
            "limit": limit,
            "offset": offset,
            "start_date": start_date,
            "end_date": end_date,
        },
    ).json()
    offset = offset + limit
    all_bookings = all_bookings + bookings
    bar.update(i)
    i += 1
    if not bookings:
        break

bar.finish()

resources_by_id = {r["id"]: r for r in all_resources}
rich_bookings = [
    {"resource": resources_by_id[b["resource_id"]], **b}
    for b in all_bookings
    if b["resource_id"] in resources_by_id
]

connection_string = os.getenv("DB_CONNECTION")

if connection_string:
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    cur.execute("begin;")
    cur.execute(
        "create table if not exists rg_log (id integer not null constraint rg_log_pkey primary key, body jsonb not null)"
    )
    cur.execute("delete from rg_log;")
    for rich_booking in progressbar.progressbar(rich_bookings):
        cur.execute(
            "insert into rg_log(id, body) values (%s, %s);",
            (rich_booking["id"], Json(rich_booking)),
        )
    cur.execute("commit;")
