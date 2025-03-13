from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, Session, relationship, DeclarativeBase
import os
# NUEVO: Importamos logging para añadir registros
import logging

# NUEVO: Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://veeam_user:veeam_password@db/factveeam")
# NUEVO: Loguear la URL de conexión (sin mostrar contraseñas)
logger.info(f"Connecting to database at: {DATABASE_URL.split('@')[1]}")

# Create FastAPI instance
app = FastAPI(title="Veeam API", description="API para gestionar datos de Veeam")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
class Base(DeclarativeBase):
    pass

# Define your database models (tables) based on the new structure
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
    # Uncomment if you add the Company_Usage class back
    # usages = relationship("Company_Usage", back_populates="company")

# Uncomment if you need the Company_Usage table
# class Company_Usage(Base):
#     __tablename__ = 'company_usage'
#     
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     company_uid = Column(String(50), ForeignKey("companies.company_uid"), nullable=False)
#     metric = Column(String(50), nullable=False)
#     metric_usage = Column(Integer, nullable=False)
#     collect_date = Column(Date, nullable=False)
#     
#     # Relación con Companies
#     company = relationship("Companies", back_populates="usages")

# NUEVO: Creamos las tablas en la base de datos
# Esta línea crea todas las tablas definidas anteriormente si no existen
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created or verified successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# NUEVO: Evento de inicio para verificar la conexión a la base de datos
@app.on_event("startup")
async def startup_db_client():
    logger.info("Application starting up...")
    try:
        db = SessionLocal()
        result = db.execute("SELECT 1").fetchone()
        logger.info(f"Database connection test successful: {result}")
        db.close()
    except Exception as e:
        logger.error(f"Error connecting to database during startup: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Veeam API - Bienvenido"}

# NUEVO: Endpoint para verificar conexión a la base de datos
@app.get("/db-check")
def check_db(db: Session = Depends(get_db)):
    try:
        # Simple query to check if DB is responding
        result = db.execute("SELECT 1").fetchone()
        # Intenta consultar las tablas para verificar que existen
        orgs_count = db.query(Organizations).count()
        companies_count = db.query(Companies).count()
        return {
            "status": "Database connection successful", 
            "result": result[0],
            "organizations_count": orgs_count,
            "companies_count": companies_count
        }
    except Exception as e:
        logger.error(f"Database check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

# Endpoints para Organizations (antes Resellers)
@app.get("/organizations/")
def read_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        organizations = db.query(Organizations).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(organizations)} organizations")
        return organizations
    except Exception as e:
        logger.error(f"Error retrieving organizations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/organizations/{organization_uid}")
def read_organization(organization_uid: str, db: Session = Depends(get_db)):
    try:
        organization = db.query(Organizations).filter(Organizations.organization_uid == organization_uid).first()
        if organization is None:
            logger.warning(f"Organization not found: {organization_uid}")
            raise HTTPException(status_code=404, detail="Organization not found")
        return organization
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving organization {organization_uid}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Endpoints para Companies
@app.get("/companies/")
def read_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        companies = db.query(Companies).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(companies)} companies")
        return companies
    except Exception as e:
        logger.error(f"Error retrieving companies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/companies/{company_uid}")
def read_company(company_uid: str, db: Session = Depends(get_db)):
    try:
        company = db.query(Companies).filter(Companies.company_uid == company_uid).first()
        if company is None:
            logger.warning(f"Company not found: {company_uid}")
            raise HTTPException(status_code=404, detail="Company not found")
        return company
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving company {company_uid}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Comentado porque la tabla Company_Usage está comentada en el modelo
# Si decides usar Company_Usage, descomenta estos endpoints
"""
# Endpoints para Company_Usage
@app.get("/usages/")
def read_usages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    usages = db.query(Company_Usage).offset(skip).limit(limit).all()
    return usages

@app.get("/companies/{company_uid}/usages")
def read_company_usages(company_uid: str, db: Session = Depends(get_db)):
    usages = db.query(Company_Usage).filter(Company_Usage.company_uid == company_uid).all()
    if not usages:
        raise HTTPException(status_code=404, detail="No usages found for this company")
    return usages
"""
