from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Advogado(Base):
    __tablename__ = "advogados"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    oab = Column(String, unique=True, index=True, nullable=False)
    cpf = Column(String, unique=True, index=True)
    email = Column(String)
    
    processos = relationship("Processo", back_populates="advogado")

class Processo(Base):
    __tablename__ = "processos"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_cnj = Column(String, unique=True, index=True, nullable=False)
    titulo = Column(String)
    cliente_nome = Column(String)
    valor_causa = Column(String) # Stored as string or Decimal
    sistema = Column(String, default="pje") # pje, esaj, eproc, etc.
    
    
    advogado_id = Column(Integer, ForeignKey("advogados.id"))
    advogado = relationship("Advogado", back_populates="processos")
    
    andamentos = relationship("Andamento", back_populates="processo")
    documentos = relationship("Documento", back_populates="processo")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Andamento(Base):
    __tablename__ = "andamentos"
    
    id = Column(Integer, primary_key=True, index=True)
    processo_id = Column(Integer, ForeignKey("processos.id"))
    data = Column(DateTime)
    descricao = Column(Text)
    conteudo = Column(Text)
    
    processo = relationship("Processo", back_populates="andamentos")

class Documento(Base):
    __tablename__ = "documentos"
    
    id = Column(Integer, primary_key=True, index=True)
    processo_id = Column(Integer, ForeignKey("processos.id"))
    titulo = Column(String)
    tipo = Column(String) # Petição, Sentença, etc.
    url_origem = Column(String) # URL no tribunal
    local_path = Column(String) # Path no storage local/cloud
    
    processo = relationship("Processo", back_populates="documentos")
    resumo = relationship("Resumo", uselist=False, back_populates="documento")

class Resumo(Base):
    __tablename__ = "resumos"
    
    id = Column(Integer, primary_key=True, index=True)
    documento_id = Column(Integer, ForeignKey("documentos.id"))
    texto_resumo = Column(Text)
    ml_model_version = Column(String)
    
    documento = relationship("Documento", back_populates="resumo")
