# Бот для оповещений пользователей

Суть проекта, что пользователи регистрируются в боте через комманду /start, а дальше через админку получает уведомления

## Запуск

docker compose up

Админка находиться на http://localhost:${FRONTEND_PORT} (по умолчанию http://localhost:9004)

## Настройки

Все конфигурационные переменные должны быть в файле .env (пример в .env.example)

## Скрипты

В папке /scripts лежат 2 скрипта, на линтинг и на типизацию

## Доп ссылки

1. [prometheus](http://localhost:9090)
2. [bot swagger](http://localhost:9000/swagger)
3. [users swagger](http://localhost:9001/swagger)
4. [notifications swagger](http://localhost:9002/swagger)
5. [proxy swagger](http://localhost:9003/swagger)
