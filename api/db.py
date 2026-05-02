import psycopg2
import psycopg2.extras
import secret_store

def get_connection():
    cfg = secret_store.get('examen2/rds')
    return psycopg2.connect(
        host=cfg['host'],
        port=cfg.get('port', 5432),
        dbname=cfg['dbname'],
        user=cfg['user'],
        password=cfg['password'],
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
