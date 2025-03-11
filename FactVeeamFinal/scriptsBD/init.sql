def create_database():
    # Configuración de la conexión
    usuario = 'veeam_user'
    contrasenya = 'veeam_password'
    host = 'localhost'  # Cuando se ejecuta dentro del contenedor
    puerto = '3306'
    nombre_base_datos = 'factveeam'

    # URL de conexión
    engine = create_engine(f'mysql+pymysql://{usuario}:{contrasenya}@{host}:{puerto}/{nombre_base_datos}')
    
    # Crear todas las tablas definidas en las clases
    Base.metadata.create_all(engine)
    print("Base de datos creada con éxito")