export $(cat .env | xargs) && cd ./apps/bot/ && poetry run python src/main.py
