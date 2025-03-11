#!/bin/bash
set -e

echo "Esperando a que MariaDB esté completamente inicializado..."
sleep 10

echo "Creando tablas con SQLAlchemy..."
cd /scriptsBD
python3 crearBD.py

echo "Insertando datos de prueba..."
python3 insertardatosBD.py

echo "Configuración de la base de datos completada."