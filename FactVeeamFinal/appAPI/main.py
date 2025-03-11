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

# Define your database models (tables)
class Resellers(Base):
    __tablename__ = 'resellers'

    reseller_uid = Column(String(50), primary_key=True, nullable=False)
    reseller_name = Column(String(100), nullable=False)
    circuit_code = Column(String(50))
    company_uid = Column(Integer)
    
    # Relación con Company
    companies = relationship("Company", back_populates="reseller")

class Company(Base):
    __tablename__ = 'companies'
    
    reseller_uid = Column(String(50), ForeignKey("resellers.reseller_uid"), primary_key=True, nullable=False)
    company_uid = Column(Integer, primary_key=True, nullable=False)
    company_name = Column(String(100), nullable=False)
    
    # Relaciones
    reseller = relationship("Resellers", back_populates="companies")
    usages = relationship("Company_Usage", back_populates="company")
    
class Company_Usage(Base):
    __tablename__ = 'company_usage'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_uid = Column(Integer, ForeignKey("companies.company_uid"), nullable=False)
    product_type = Column(String(50), nullable=False)
    license_type = Column(String(50), nullable=False)
    usage = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    
    # Relación con Company
    company = relationship("Company", back_populates="usages")

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

# Endpoints para Resellers
@app.get("/resellers/")
def read_resellers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    resellers = db.query(Resellers).offset(skip).limit(limit).all()
    return resellers

@app.get("/resellers/{reseller_uid}")
def read_reseller(reseller_uid: str, db: Session = Depends(get_db)):
    reseller = db.query(Resellers).filter(Resellers.reseller_uid == reseller_uid).first()
    if reseller is None:
        raise HTTPException(status_code=404, detail="Reseller not found")
    return reseller

# Endpoints para Companies
@app.get("/companies/")
def read_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    companies = db.query(Company).offset(skip).limit(limit).all()
    return companies

@app.get("/companies/{company_uid}")
def read_company(company_uid: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.company_uid == company_uid).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

# Endpoints para Company_Usage
@app.get("/usages/")
def read_usages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    usages = db.query(Company_Usage).offset(skip).limit(limit).all()
    return usages

@app.get("/companies/{company_uid}/usages")
def read_company_usages(company_uid: int, db: Session = Depends(get_db)):
    usages = db.query(Company_Usage).filter(Company_Usage.company_uid == company_uid).all()
    if not usages:
        raise HTTPException(status_code=404, detail="No usages found for this company")
    return usages