from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Classe base para todos os models ORM do sistema.
    Toda entidade (Cliente, Quarto, Reserva) herda desta classe.
    O SQLAlchemy usa ela para registrar e mapear as classes como tabelas.
    """
    pass
