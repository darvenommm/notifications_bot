export $(cat .env | xargs) && cd ./apps/users/ && poetry run python src/main.py
