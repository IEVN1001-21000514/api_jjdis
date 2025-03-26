class DevelopmentConfig():
    DEBUG = True
    MYSQL_HOST = 'sql207.infinityfree.com'
    MYSQL_USER = 'if0_38604025'
    MYSQL_PASSWORD = '22Kevin100202'  # Cambia si tienes contraseña en MySQL
    MYSQL_DB = 'if0_38604025_XXX'  # Asegúrate de que este nombre coincida con tu base de datos

config = {
    'development': DevelopmentConfig
}