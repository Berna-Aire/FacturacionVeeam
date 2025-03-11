from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import json
import os
from crearBD import Base, Organizations, Companies

def insert_data_from_json(session, json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        print(f"Datos cargados desde {json_file_path}")
        
        # Diccionario para rastrear las organizaciones ya insertadas (para evitar duplicados)
        inserted_organizations = {}
        
        # Primero, extraer las organizaciones únicas de los datos del JSON
        # En el JSON las organizaciones son llamadas "resellers"
        for reseller in data['resellers']:
            org_uid = reseller['reseller_uid']
            if org_uid not in inserted_organizations:
                org_entry = Organizations(
                    organization_uid=org_uid,
                    organization_name=reseller['reseller_name'],
                    tax_id=reseller['tax_id'],
                    company_id=str(reseller.get('company_uid', ''))  # Opcional, usar cadena vacía si no existe
                )
                session.add(org_entry)
                inserted_organizations[org_uid] = org_entry
                
        session.flush()  # Asegurarse de que las organizaciones se guardan antes de añadir compañías
        print(f"Organizaciones insertadas: {len(inserted_organizations)}")

        # Insertar datos en la tabla Companies
        companies_count = 0
        for company in data['companies']:
            # Verificar que la organización (reseller) existe
            if company['reseller_uid'] in inserted_organizations:
                company_entry = Companies(
                    company_uid=str(company['company_uid']),  # Convertir a string según la definición de la tabla
                    company_name=company['company_name'],
                    organization_uid=company['reseller_uid']
                )
                session.add(company_entry)
                companies_count += 1
            else:
                print(f"Advertencia: Organización con UID {company['reseller_uid']} no encontrada para la compañía {company['company_name']}")
        
        # Hacer commit de todos los cambios
        session.commit()
        print(f"Compañías insertadas: {companies_count}")
        print("Datos insertados correctamente en la base de datos")
        
    except Exception as e:
        session.rollback()
        print(f"Error al insertar datos: {str(e)}")
        raise

def query_data(session):
    try:
        # Consultar todas las organizaciones
        organizations = session.query(Organizations).all()
        print(f"\nOrganizaciones encontradas: {len(organizations)}")
        for org in organizations:
            print(f"  - {org.organization_name} (UID: {org.organization_uid}, Tax ID: {org.tax_id})")

        # Consultar todas las compañías
        companies = session.query(Companies).all()
        print(f"\nCompañías encontradas: {len(companies)}")
        for company in companies:
            print(f"  - {company.company_name} (UID: {company.company_uid}, Org UID: {company.organization_uid})")
    
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
