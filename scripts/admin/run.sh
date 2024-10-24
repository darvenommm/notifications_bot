export $(cat .env | xargs) && cd ./apps/admin/ && poetry run python src/main.py
