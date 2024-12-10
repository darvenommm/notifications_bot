from prometheus_client import Counter, Histogram


HTTP_REQUEST_TOTAL = Counter(
    "http_requests_total", "Total number of HTTP requests", ["server", "method", "path"]
)

HTTP_REQUEST_SUCCESS_TOTAL = Counter(
    "http_requests_success_total",
    "Total number of success HTTP requests",
    ["server", "method", "path", "status"],
)

RECEIVED_BROKER_MESSAGES_TOTAL = Counter(
    "received_messages_total",
    "Total number of received messages by the consumer",
    ["consumer", "provider", "title"],
)

SENDED_BROKER_MESSAGES_TOTAL = Counter(
    "sended_messages_total",
    "Total number of sended messages by the provider",
    ["provider", "consumer", "title"],
)

# I'm satisfied with the default buckets
DATABASE_REQUEST_DURATION_SECONDS = Histogram(
    "database_request_duration_seconds",
    "Histogram of database request durations in seconds",
    ["server", "handler"],
)

AIOGRAM_REQUEST_DURATION_SECONDS = Histogram(
    "aiogram_request_duration_seconds",
    "Histogram of aiogram handler durations in seconds",
    ["server", "handler"],
)
