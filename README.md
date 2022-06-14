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

Copy `.env.sample` to `.env`
