# HeadLine

## Install

Install Python dependencies in your virtual environment

```sh
pip install -r requirements.txt
```

## Run

Run

```sh
# On Mac or Linux
./headline/main.py

# On Win
python3 headline\main.py
```

Note: If you receive an error similar to `ModuleNotFoundError: No module named 'headline'`,
it's because your IDE didn't properly set PYTHONPATH so run:

```sh
export PYTHONPATH=$(pwd)
```

## Config

Copy `.env.sample` to `.env` and fill the appropriate environmental variables.

For each *OAuth2* provider you have to provide a `client_id` and `client_secret`, to do so,
create 2 environmental variable for each auth provider with the format `<NAME>_CLIENT_ID`
and `<NAME>_CLIENT_SECRET`, for example:

```env
GOOGLE_CLIENT_ID=client_id here
GOOGLE_CLIENT_SECRET=client_secret here
```

> Note: Google Auth provider covers both GMail and Google Calendar
