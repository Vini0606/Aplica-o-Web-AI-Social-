from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker # Adicione sessionmaker
from sqlalchemy_utils.types import ChoiceType

# Cria a conexão do seu Banco
db = create_engine("sqlite:///banco.db")

# cria base do banco de dados
Base = declarative_base()

# Criar as classes\tabelas do banco
class Usuario(Base):
    __tablename__="usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String)
    email = Column("email", String, nullable=False, unique=True) # E-mail deve ser único
    senha = Column("senha", String, nullable=False) # Senha hashed
    ativo = Column("ativo", Boolean, default=True)
    admin = Column("admin", Boolean, default=False)

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email = email
        self.senha = senha # Lembre-se: hash antes de salvar!
        self.ativo = ativo
        self.admin = admin

# Criar as classes\tabelas do banco
class Pedido(Base):
    __tablename__="pedidos"

    STATUS_PEDIDOS = (
            ("PENDENTE", "PENDENTE"),
            ("CANCELADO", "CANCELADO"),
            ("FINALIZADO", "FINALIZADO")
    )

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    # Correção de typo: "satus" para "status"
    status = Column("status", ChoiceType(choices=STATUS_PEDIDOS), default="PENDENTE") # pendente, cancelado, finalizado
    usuario = Column("usuario", ForeignKey("usuarios.id"), nullable=False)
    # Correção de typo: "senha" para "preco"
    preco = Column("preco", Float)

    def __init__(self, usuario, status="PENDENTE", preco=0):

        self.status = status
        self.usuario = usuario
        self.preco = preco

class ItemPedido(Base):
    __tablename__="itens_pedidos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantidade = Column("quantidade", Integer)
    sabor = Column("sabor", String)
    tamanho = Column("tamanho", String)
    preco_unitario = Column("preco_unitario", Float)
    pedido = Column("pedido", ForeignKey("pedidos.id"))

    def __init__(self, quantidade, sabor, tamanho, preco_unitario, pedido):

        self.quantidade = quantidade
        self.sabor = sabor
        self.tamanho = tamanho
        self.preco_unitario = preco_unitario
        self.pedido = pedido

# Crie uma sessão do banco de dados (novo)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db)

# Função para obter a sessão do banco de dados (novo)
def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

# Crie as tabelas no banco de dados (novo - para ser chamado uma vez no startup)
def create_db_tables():
    Base.metadata.create_all(bind=db)