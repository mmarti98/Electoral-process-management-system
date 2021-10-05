import os;

databaseUrl = os.environ["DATABASE_URL"]

class Configuration ( ):
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/elections";
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    REDIS_HOST = "localhost";
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'