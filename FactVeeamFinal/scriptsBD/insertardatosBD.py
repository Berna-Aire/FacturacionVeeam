from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from faker import Faker
import random
import json
import os
import datetime
from crearBD import Base, Resellers, Company, Company_Usage

# Inicializar Faker
fake = Faker()

# Función para generar datos desde un JSON
def insert_data_from_json(session, json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        print(f"Datos cargados desde {json_file_path}")
        
        # Insertar datos en la tabla Resellers
        for reseller in data['resellers']:
            reseller_entry = Resellers(
                reseller_uid=reseller['reseller_uid'],
                reseller_name=reseller['reseller_name'],
                circuit_code=str(random.randint(1000, 9999)),  # Código aleatorio
                company_uid=random.randint(1, 100)  # ID aleatorio
            )
            session.add(reseller_entry)
        
        session.flush()  # Asegurarse de que los resellers se guardan antes de añadir companies
        print(f"Resellers insertados: {len(data['resellers'])}")

        # Insertar datos en la tabla Companies
        for company in data['companies']:
            company_entry = Company(
                reseller_uid=company['reseller_uid'],
                company_uid=company['company_uid'],
                company_name=company['company_name']
            )
            session.add(company_entry)
        
        session.flush()  # Asegurarse de que las companies se guardan antes de añadir usages
        print(f"Companies insertadas: {len(data['companies'])}")

        # Insertar datos en la tabla Company_Usage
        for company in data['companies']:
            # Generamos varios registros de uso por compañía
            for _ in range(3):  # 3 registros de uso por compañía
                usage_entry = Company_Usage(
                    company_uid=company['company_uid'],
                    product_type=random.choice(["VBR", "VBO365", "Kasten"]),
                    license_type=random.choice(["Perpetual", "Subscription", "Community"]),
                    usage=company.get('metric_usage', random.randint(1, 1000)),
                    date=datetime.date(2024, random.randint(1, 12), random.randint(1, 28))
                )
                session.add(usage_entry)
        
        # Hacer commit de todos los cambios
        session.commit()
        print("Datos insertados correctamente en la base de datos")
        
    except Exception as e:
        session.rollback()
        print(f"Error al insertar datos: {str(e)}")
        raise

def query_data(session):
    try:
        # Consultar todos los resellers
        resellers = session.query(Resellers).all()
        print(f"\nResellers encontrados: {len(resellers)}")
        for reseller in resellers[:3]:  # Mostrar solo los primeros 3 para no saturar
            print(f"  - {reseller.reseller_name} (ID: {reseller.reseller_uid})")

        # Consultar todas las companies
        companies = session.query(Company).all()
        print(f"\nCompanies encontradas: {len(companies)}")
        for company in companies[:3]:  # Mostrar solo las primeras 3
            print(f"  - {company.company_name} (ID: {company.company_uid}, Reseller: {company.reseller_uid})")

        # Consultar todos los company usages
        usages = session.query(Company_Usage).all()
        print(f"\nUsages encontrados: {len(usages)}")
        for usage in usages[:3]:  # Mostrar solo los primeros 3
            print(f"  - Company ID: {usage.company_uid}, Product: {usage.product_type}, Usage: {usage.usage}")
    
    except Exception as e:
        print(f"Error al consultar datos: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # Configuración de la conexión
        usuario = 'veeam_user'
        contrasenya = 'veeam_password'
        host = 'localhost'
        puerto = '3306'
        nombre_base_datos = 'factveeam'

        # URL de conexión
        engine = create_engine(f'mysql+pymysql://{usuario}:{contrasenya}@{host}:{puerto}/{nombre_base_datos}', 
                             pool_pre_ping=True, 
                             echo=True)  # echo=True para ver las consultas SQL
        
        # Crear una sesión
        with Session(engine) as session:
            # Determinar la ruta del archivo JSON
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_file_path = os.path.join(current_dir, 'datosprueba.json')
            
            # Comprobar si el archivo existe
            if not os.path.exists(json_file_path):
                # Intentar con la ruta relativa
                json_file_path = 'datosprueba.json'
                if not os.path.exists(json_file_path):
                    print(f"No se pudo encontrar el archivo JSON en {json_file_path}")
                    exit(1)
            
            # Insertar datos desde el JSON
            insert_data_from_json(session, json_file_path)
            
            # Realizar consultas para verificar
            query_data(session)
            
            print("Proceso completado con éxito")
    
    except Exception as e:
        print(f"Error general: {str(e)}")