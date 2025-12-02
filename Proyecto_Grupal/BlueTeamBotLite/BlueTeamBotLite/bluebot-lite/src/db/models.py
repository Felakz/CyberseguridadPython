from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from pathlib import Path

Base = declarative_base()

class Scan(Base):
    """Tabla de escaneos realizados"""
    __tablename__ = 'scans'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(Integer, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    total_findings = Column(Integer, default=0)
    duration_seconds = Column(Integer, default=0)
    
    findings = relationship("Finding", back_populates="scan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Scan(id={self.id}, timestamp={self.timestamp}, findings={self.total_findings})>"


class Finding(Base):
    """Tabla de hallazgos de seguridad"""
    __tablename__ = 'findings'
    
    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey('scans.id'), nullable=False, index=True)
    
    host = Column(String(50), nullable=False, index=True)
    port = Column(Integer, nullable=False)
    service = Column(String(50))
    product = Column(String(100))
    version = Column(String(50))
    env = Column(String(20))
    
    severity = Column(String(10), index=True)  # HIGH, MEDIUM, LOW
    reasons = Column(Text)  # JSON array serializado
    status = Column(String(10))  # NEW, CHANGED, SAME
    
    scan = relationship("Scan", back_populates="findings")
    
    def __repr__(self):
        return f"<Finding(host={self.host}, port={self.port}, severity={self.severity})>"


# Configuración global
DB_PATH = Path("data/bluebot.db")
_engine = None
_SessionLocal = None


def init_db():
    """Inicializa la base de datos y crea las tablas"""
    global _engine, _SessionLocal
    
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
        Base.metadata.create_all(_engine)
        _SessionLocal = sessionmaker(bind=_engine)
        print(f"[DB] Base de datos inicializada en {DB_PATH}")
        return _engine
    except Exception as e:
        print(f"[DB ERROR] Error inicializando base de datos: {e}")
        raise


def get_session():
    """Devuelve una nueva sesión de base de datos"""
    global _SessionLocal
    
    if _SessionLocal is None:
        init_db()
    
    if _SessionLocal is None:
        raise RuntimeError(
            "No se pudo inicializar la sesión de base de datos. "
            "Verifica que init_db() esté configurando _SessionLocal correctamente."
        )
    
    return _SessionLocal()
