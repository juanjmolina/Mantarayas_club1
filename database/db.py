conn = psycopg2.connect(
    url,
    sslmode="require",
    connect_timeout=10,
)
