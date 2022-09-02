from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import URL
from sqlalchemy import Column, String, Integer, Boolean, Float, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import URL
from sqlalchemy import Column, String, Integer, Boolean, Float, DateTime, ForeignKey, join, select, insert, update
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os




#Conexao HauszMapa
import pyodbc
from sqlalchemy import create_engine
import dotenv
dotenv.load_dotenv(dotenv.find_dotenv())

Server = os.getenv('server')
usuario = os.getenv('UID')
tabela = os.getenv('Database')
password = os.getenv('PWD')




connection_url = URL.create(
    "mssql+pyodbc",
    username=f"{usuario}",
    password=f"4PL1C4ÇAO_3STOQUF202#",
    host=f"{Server}",
    database=f"{tabela}",
    query={
        "driver": "ODBC Driver 17 for SQL Server",
        "autocommit": "True",
    },
)


def get_engine():
    engine = create_engine(connection_url).execution_options(
        isolation_level="AUTOCOMMIT", future=True
    )
    return engine

Base = declarative_base()
Session = sessionmaker(bind=get_engine())
session = Session()


class ProdutosSaldos(Base):
    __tablename__ = "ProdutosSaldos"
    __table_args__ = {"schema": "Produtos"}
    IdProdutosSaldos = Column(Integer, primary_key=True)
    SKU = Column(String(1000), unique=False, nullable=False)
    IdMarca = Column(Integer)
    Quantidade = Column(Float)
    DataAtualizado = Column(DateTime, unique=False, nullable=False)



class ProdutoPrazoProducFornec(Base):
    __tablename__ = "ProdutoPrazoProducFornec"
    __table_args__ = {"schema": "Produtos"}
    IdPrazos = Column(Integer, primary_key=True)
    SKU = Column(String(1000), unique=False, nullable=False)
    PrazoEstoqueFabrica = Column(Float)
    PrazoProducao = Column(Float)
    PrazoOperacional = Column(Float)
    PrazoFaturamento = Column(Float)
    PrazoTotal = Column(Float)
   


    def __repr__(self):
        return f'{self.SKU}'


class LogEstoqueFornecedor(Base):
    __tablename__="LogEstoqueFornecedor"
    __table_args__ = {"schema": "Produtos"}
    IdLogEstoqueFornec = Column(Integer, primary_key=True)
    IdUsuario = Column(Integer)
    SKU = Column(String, unique=False, nullable=False)
    IdMarca = Column(Integer,unique=False, nullable=False)
    IdTipo  = Column(Integer,unique=False, nullable=False)
    ValorAnterio = Column(Float,unique=False, nullable=False)
    ValorAlterado = Column(Float,unique=False, nullable=False)
    PrazoProducaoAnterior = Column(Integer,unique=False, nullable=False)
    PrazoProducaoAlterado = Column(Integer,unique=False, nullable=False)
    DataAlteracao = Column(DateTime, unique=False, nullable=False)



