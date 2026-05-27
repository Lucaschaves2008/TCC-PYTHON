from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from models.base import Base


class Cliente(Base):
    """
    Entidade que representa um hóspede do hotel.

    No banco de dados, cada instância desta classe é uma linha na tabela 'clientes'.
    Os atributos da classe (id, nome, email...) mapeiam diretamente para colunas SQL.
    """

    __tablename__ = "clientes"

    # --- COLUNAS DA TABELA ---

    # Chave primária: gerada automaticamente pelo banco (autoincrement)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Nome completo: obrigatório (nullable=False), até 100 caracteres
    nome = Column(String(100), nullable=False)

    # Email: obrigatório e único (não pode ter dois clientes com o mesmo email)
    email = Column(String(150), nullable=False, unique=True)

    # Telefone: opcional (nullable=True)
    telefone = Column(String(20), nullable=True)

    # CPF: obrigatório e único
    cpf = Column(String(14), nullable=False, unique=True)

    # Timestamps: preenchidos automaticamente pelo SQLAlchemy
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # --- RELACIONAMENTOS ---

    # Um Cliente pode ter várias Reservas.
    # 'back_populates' cria o link bidirecional: reserva.cliente também funciona.
    # cascade="all, delete-orphan": se o cliente for deletado, as reservas dele
    # também são removidas automaticamente.
    reservas = relationship(
        "Reserva",
        back_populates="cliente",
        cascade="all, delete-orphan",
    )

    # --- MÉTODOS ESPECIAIS ---

    def __repr__(self) -> str:
        """Representação legível no terminal para debug."""
        return f"<Cliente(id={self.id}, nome='{self.nome}', cpf='{self.cpf}')>"

    def to_dict(self) -> dict:
        """
        Converte o objeto para dicionário Python.
        Necessário para passar dados ao Streamlit (que trabalha com dicts e DataFrames).
        """
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "telefone": self.telefone or "",
            "cpf": self.cpf,
            "created_at": self.created_at.strftime("%d/%m/%Y %H:%M") if self.created_at else "",
            "updated_at": self.updated_at.strftime("%d/%m/%Y %H:%M") if self.updated_at else "",
        }
