from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship, declarative_base

# Usar la versión actualizada del import para evitar la advertencia
Base = declarative_base()

class Organizations(Base):
    __tablename__ = 'organizations'

    organization_uid = Column(String(50), primary_key=True)
    organization_name = Column(String(100))
    tax_id = Column(String(50))
    company_id = Column(String(50))
    
    # Relación con Companies
    companies = relationship("Companies", back_populates="organization")

class Companies(Base):
    __tablename__ = 'companies'
    
    company_uid = Column(String(50), primary_key=True)
    company_name = Column(String(100), nullable=False)
    organization_uid = Column(String(50), ForeignKey("organizations.organization_uid"), nullable=False)
    
    # Relaciones
    organization = relationship("Organizations", back_populates="companies")
    #usages = relationship("Company_Usage", back_populates="company")
    
#class Company_Usage(Base):
    #__tablename__ = 'company_usage'
#    
    ## Crear un ID autoincrementable como clave primaria para evitar problemas con la clave foránea
    #id = Column(Integer, primary_key=True, autoincrement=True)
    #company_uid = Column(String(50), ForeignKey("companies.company_uid"), nullable=False)
    #metric = Column(String(50), nullable=False)
    #metric_usage = Column(Integer, nullable=False)
    #collect_date = Column(Date, nullable=False)
#    
    ## Relación con Companies
    #company = relationship("Companies", back_populates="usages")

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

if __name__ == "__main__":
    create_database()