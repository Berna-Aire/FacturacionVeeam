#!/bin/sh
set -e

host="$1"
shift

echo "Esperando a que la base de datos en $host esté disponible..."

# Esperar a que MySQL esté disponible
until mysql -h "$host" -u veeam_user -pveeam_password -e 'SELECT 1' > /dev/null 2>&1; do
  echo "MySQL en $host todavía no está disponible - esperando..."
  sleep 2
done

echo "MySQL en $host está disponible - continuando"

# Ejecutar el comando
exec "$@"