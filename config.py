class DevelopmentConfig():
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''  # Cambia si tienes contraseña en MySQL
    MYSQL_DB = 'jjdis'  # Asegúrate de que este nombre coincida con tu base de datos

config = {
    'development': DevelopmentConfig
}