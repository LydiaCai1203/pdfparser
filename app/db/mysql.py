from config import config


if hasattr(config, "mysql"):
    MYSQL_URL = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset={charset}".format(
        username=config.mysql.username,
        password=config.mysql.password,
        host=config.mysql.host,
        port=config.mysql.port,
        db=config.mysql.database,
        charset=config.mysql.charset
    )
else:
    MYSQL_URL = ""

def ping_db() -> bool:
    return False


def init_db(engine) -> str:
    return "Success"
