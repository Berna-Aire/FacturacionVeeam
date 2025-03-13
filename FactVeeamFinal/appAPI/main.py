from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import os

# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://veeam_user:veeam_password@db/factveeam")

# Create FastAPI instance
app = FastAPI(title="Veeam API", description="API para gestionar datos de Veeam")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Veeam API - Bienvenido"}

# Endpoints para Organizations (antes Resellers)
@app.get("/organizations/")
def read_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    organizations = db.query(Organizations).offset(skip).limit(limit).all()
    return organizations

@app.get("/organizations/{organization_uid}")
def read_organization(organization_uid: str, db: Session = Depends(get_db)):
    organization = db.query(Organizations).filter(Organizations.organization_uid == organization_uid).first()
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization

# Endpoints para Companies
@app.get("/companies/")
def read_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    companies = db.query(Companies).offset(skip).limit(limit).all()
    return companies

@app.get("/companies/{company_uid}")
def read_company(company_uid: str, db: Session = Depends(get_db)):
    company = db.query(Companies).filter(Companies.company_uid == company_uid).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

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
