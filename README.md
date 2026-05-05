# ДЗ 2 семестр 2 - сравнение двух версий системы обработки задач

## Установка
```shell
uv sync
cp .env.example .env
```

## Запуск
Запускаем `RabbitMQ`
```shell
sudo docker compose up -d
```

Активируем виртуальное окружение для своего терминала (у меня fish)
```shell
source .venv/bin/activate.fish
```

Запускаем `FastAPI` сервер
```shell
fastapi dev src/api/main.py
```

Запускаем воркер для обработки задач из очереди
```shell
uv run python -m worker
```