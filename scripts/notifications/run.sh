export $(cat .env | xargs) && cd ./apps/notifications/ && poetry run python src/main.py
