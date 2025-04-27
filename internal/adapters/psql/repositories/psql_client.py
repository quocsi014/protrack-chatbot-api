from config import AppConfig
import psycopg2


def create_conn(cfg: AppConfig):
    return psycopg2.connect(
        host=cfg.PSQL_HOST,
        port=cfg.PSQL_PORT,
        database=cfg.PSQL_DB,
        user=cfg.PSQL_USER,
        password=cfg.PSQL_PSSWD
    )
