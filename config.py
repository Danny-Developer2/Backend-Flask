# from datetime import timedelta

# class Config:
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     JSON_SORT_KEYS = False


from datetime import timedelta

class Config:
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://sa:TuPasswordSegura123@localhost:1433/master?driver=ODBC+Driver+17+for+SQL+Server'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'tu-clave-secreta-aqui'
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_CHECK_FORM = True
    JWT_ACCESS_COOKIE_NAME = 'access_token'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)


    
def __init__(self):
        print(f"Using database URI: {self.SQLALCHEMY_DATABASE_URI}")