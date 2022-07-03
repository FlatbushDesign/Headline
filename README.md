# HeadLine

## Install

Install Python dependencies in your virtual environment

```sh
pip install -r requirements.txt
```

## Run

Run the server

```sh
uvicorn headline.app:app --reload
```

Run the client

```sh
cd static
python -m http.server 3000
```

## Config

Copy `.env.sample` to `.env` and fill the appropriate environmental variables.

For each _OAuth2_ provider you have to provide a `client_id` and `client_secret`, to do so,
create 2 environmental variable for each auth provider with the format `<NAME>_CLIENT_ID`
and `<NAME>_CLIENT_SECRET`, for example:

```env
GOOGLE_CLIENT_ID=client_id here
GOOGLE_CLIENT_SECRET=client_secret here
```

> Note: Google Auth provider covers both GMail and Google Calendar

## Deploy

Front-end:

```sh
firebase deploy
```

Back-end:

```sh
gcloud app deploy app.yaml cron.yaml
```
