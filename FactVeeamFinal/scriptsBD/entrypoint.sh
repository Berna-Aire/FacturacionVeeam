#!/bin/bash
set -e

# Iniciar el servicio de MariaDB
docker-entrypoint.sh mysqld &

# Esperar a que MariaDB esté listo
until mysqladmin ping -h localhost -u root -p$MYSQL_ROOT_PASSWORD --silent; do
    echo "Esperando a que MariaDB esté disponible..."
    sleep 2
done

echo "MariaDB está disponible, ejecutando scripts de inicialización..."

# Ir al directorio de scripts y ejecutar la creación de la BD
cd /scriptsBD
python3 crearBD.py

# Ejecutar script para insertar datos de prueba
python3 insertardatosBD.py

# Mantener el contenedor en ejecución
wait