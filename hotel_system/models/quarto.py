import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Integer, Numeric, String
from sqlalchemy.orm import relationship

from models.base import Base


# --- ENUMS ---
# Enums definem listas fechadas de valores permitidos.
# O Python e o MySQL validam juntos: nenhum valor fora da lista é aceito.

class StatusQuarto(str, enum.Enum):
    """Status operacional do quarto."""
    DISPONIVEL = "disponivel"
    OCUPADO    = "ocupado"
    MANUTENCAO = "manutencao"


class TipoQuarto(str, enum.Enum):
    """Categoria/tipo do quarto."""
    SOLTEIRO = "solteiro"
    CASAL    = "casal"
    LUXO     = "luxo"
    SUITE    = "suite"


# --- ENTIDADE ---

class Quarto(Base):
    """
    Entidade que representa um quarto físico do hotel.

    O status do quarto muda conforme o ciclo de reservas:
    DISPONIVEL → (nova reserva) → OCUPADO → (checkout) → DISPONIVEL
    DISPONIVEL → (problema) → MANUTENCAO → (resolvido) → DISPONIVEL
    """

    __tablename__ = "quartos"

    # --- COLUNAS DA TABELA ---

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Número do quarto: é uma string para suportar formatos como "101A", "PH1"
    numero = Column(String(10), nullable=False, unique=True)

    # Tipo usa o Enum TipoQuarto — só aceita os 4 valores definidos acima
    tipo = Column(Enum(TipoQuarto), nullable=False)

    # Status começa como DISPONIVEL por padrão ao criar um quarto
    status = Column(
        Enum(StatusQuarto),
        nullable=False,
        default=StatusQuarto.DISPONIVEL,
    )

    # Capacidade máxima de pessoas
    capacidade = Column(Integer, nullable=False, default=1)

    # Preço da diária: Numeric(10, 2) = até 10 dígitos, 2 casas decimais
    # Exemplo: 99999999.99 — nunca use Float para dinheiro (erro de arredondamento)
    preco_diaria = Column(Numeric(10, 2), nullable=False)

    # Descrição opcional do quarto
    descricao = Column(String(300), nullable=True)

    # Timestamps automáticos
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # --- RELACIONAMENTOS ---

    # Um Quarto pode estar em várias Reservas (ao longo do tempo)
    reservas = relationship("Reserva", back_populates="quarto")

    # --- MÉTODOS ESPECIAIS ---

    def __repr__(self) -> str:
        return (
            f"<Quarto(numero='{self.numero}', tipo={self.tipo.value}, "
            f"status={self.status.value}, diaria=R${self.preco_diaria})>"
        )

    def esta_disponivel(self) -> bool:
        """Verifica se o quarto está disponível para reserva."""
        return self.status == StatusQuarto.DISPONIVEL

    def to_dict(self) -> dict:
        """Converte o objeto para dicionário — usado pelo Streamlit."""
        return {
            "id": self.id,
            "numero": self.numero,
            "tipo": self.tipo.value,
            "status": self.status.value,
            "capacidade": self.capacidade,
            "preco_diaria": float(self.preco_diaria),
            "descricao": self.descricao or "",
            "created_at": self.created_at.strftime("%d/%m/%Y %H:%M") if self.created_at else "",
        }
